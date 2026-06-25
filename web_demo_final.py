import os
import torch
import gradio as gr
import json
import re
import sys
import datetime
import requests
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# ================= 0. 路径适配逻辑 =================
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 导入 Agent 1 工具和 Agent 2 归档逻辑
try:
    from Agent1.tools import TOOL_FUNCTIONS
    from Agent2.main_agent import archivist_agent_logic 
    print("✅ 成功加载 Agent1 工具库与 Agent2 归档模块")
except ImportError as e:
    print(f"❌ 导入失败，请检查文件夹下是否有 __init__.py 文件！错误信息: {e}")
    sys.exit(1)

# ================= 1. 模型加载 =================
BASE_MODEL_PATH = "/root/autodl-tmp/Qwen2.5-0.5B-Instruct"
LORA_PATH = "/root/autodl-tmp/Travel_Agent_Project/output/travel_lora"

print("🚀 正在载入金牌导游系统大脑...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH, 
    torch_dtype=torch.float16, 
    device_map="auto"
)

if os.path.exists(LORA_PATH):
    print("✨ 检测到微调权重，正在融合 LoRA...")
    model = PeftModel.from_pretrained(base_model, LORA_PATH)
else:
    print("⚠️ 未发现微调权重，使用基础模型运行...")
    model = base_model
model = model.eval()


# ================= 2. Agent 1 专用解析器 =================
def extract_action(model_output, user_message):
    action_match = re.search(r"Action[:：]\s*(\w+|[\u4e00-\u9fa5]+)", model_output)
    args_match = re.search(r"Args[:：]\s*({.*?})", model_output)
    
    act = None
    arg_json = None

    if action_match and args_match:
        act = action_match.group(1).strip()
        arg_json = args_match.group(1).strip()
        mapping = {
            "天气": "get_weather", "查询天气": "get_weather",
            "地图": "get_map_route", "规划路线": "get_map_route", "路线": "get_map_route",
            "搜索": "search_attractions", "攻略": "search_attractions", "景点信息": "search_attractions"
        }
        act = mapping.get(act, act)
        try:
            params = json.loads(arg_json)
            new_params = {}
            for k, v in params.items():
                k_map = {"城市": "city", "地点": "location", "起点": "origin", "终点": "destination"}
                new_params[k_map.get(k, k)] = v
            arg_json = json.dumps(new_params)
        except: pass

    if not act or act not in TOOL_FUNCTIONS:
        cities = ["北京", "上海", "广州", "成都", "杭州", "西安", "南京", "厦门", "武汉", "苏州", "重庆"]
        found_city = "北京"
        for c in cities:
            if c in user_message: found_city = c; break
        if any(w in user_message for w in ["攻略", "规划", "玩", "推荐"]):
            return "search_attractions", json.dumps({"city": found_city, "keywords": "热门景点推荐"})
        if "天气" in user_message:
            return "get_weather", json.dumps({"city": found_city})
    
    return act, arg_json

# ================= 3. 多智能体预测流 (逻辑修正版) =================
def agent_predict(message, history):
    thought_log = []

    # --- 逻辑 1: 检测归档指令 (Agent 2 逻辑) ---
    save_keywords = ["归档", "保存", "存一下", "记录一下", "save", "archive"]
    if any(kw in message for kw in save_keywords):
        thought_log.append("🤖 [Agent 2] 检测到归档意图，正在检索上一轮生成的方案...")
        
        # 【核心修正】：在 Gradio 中，当前对话已追加，所以上一轮 bot 回复在 history[-2][1]
        last_plan_content = ""
        if len(history) >= 2:
            last_plan_content = history[-2][1]
        
        # 校验：必须包含导游回复的特征字符
        if not last_plan_content or "亲爱的游客" not in last_plan_content:
            yield "抱歉，我没有在对话记录中找到可以归档的旅行方案。请先让我为您规划一个行程吧！", thought_log
            return

        yield "方案已找到，正在执行本地数字化归档...", thought_log
        
        # 提取城市名用于命名 (从攻略内容中抓取)
        city_match = re.search(r"(北京|上海|广州|成都|杭州|西安|南京|厦门|武汉|重庆|苏州)", last_plan_content)
        city_name = city_match.group(1) if city_match else "旅行规划"
        
        # 清洗掉攻略末尾的提示语，只保存纯净内容
        clean_content = last_plan_content.split("---")[0].strip()
        
        # 调用 Agent 2 执行归档
        save_status = archivist_agent_logic(clean_content, city_name)
        
        thought_log.append(f"📁 {save_status}")
        yield f"【系统消息】{save_status}", thought_log
        return

    # --- 逻辑 2: 护栏拦截 ---
    illegal_keywords = ["数学", "编程", "解方程", "考试", "作业"]
    if any(word in message for word in illegal_keywords):
        yield "抱歉，亲爱的游客。我目前只能处理旅游相关的咨询。您可以问我关于目的地的问题呀！", []
        return

    # ======= 🤖 [Agent 1] 工作开始：规划与创作 =======
    thought_log.append("🤖 [Agent 1] 正在分析您的旅行需求...")
    prompt = f"<|im_start|>system\n你是一个专业的旅行管家。请输出 Action: 工具名, Args: {{\"参数\": \"值\"}}<|im_end|>\n<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n思考："
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    input_len = inputs.input_ids.shape[1]
    
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=80, temperature=0.1)
        gen_text = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
    
    action, args_str = extract_action(gen_text, message)
    
    if action:
        try:
            args = json.loads(args_str)
            city = args.get("city", "未知城市")
            
            thought_log.append(f"🛠️ [Agent 1] 正在调取 {city} 的实时数据素材...")
            yield "正在同步调取外部 API 数据...", thought_log
            
            # 执行工具
            weather_data = TOOL_FUNCTIONS["get_weather"](city=city)
            search_data = TOOL_FUNCTIONS["search_attractions"](city=city, keywords="热门攻略")
            observation = f"【实时气象】: {weather_data}\n【当地攻略】: {search_data}"
            
            thought_log.append("✅ [Agent 1] 素材已汇总，正在撰写深度长文攻略...")
            
            # 生成长文
            sum_prompt = f"<|im_start|>system\n你是一位金牌导游。根据素材写攻略，必须包含天气、美食和Markdown表格。语气要热情。<|im_end|>\n<|im_start|>user\n素材：{observation}\n需求：{message}<|im_end|>\n<|im_start|>assistant\n亲爱的游客您好！"
            sum_inputs = tokenizer(sum_prompt, return_tensors="pt").to("cuda")
            sum_in_len = sum_inputs.input_ids.shape[1]
            
            with torch.no_grad():
                sum_outputs = model.generate(**sum_inputs, max_new_tokens=800, temperature=0.7, repetition_penalty=1.1)
                final_answer = "亲爱的游客您好！" + tokenizer.decode(sum_outputs[0][sum_in_len:], skip_special_tokens=True)
            
            # 只有 Agent 1 的回答，并在末尾添加归档提示
            final_answer_with_hint = final_answer.strip() + "\n\n---\n💡 **小贴士**：如果您喜欢这份方案，请输入“**帮我归档**”，我将为您保存为本地文件。"
            yield final_answer_with_hint, thought_log

        except Exception as e:
            yield f"抱歉，系统在协作过程中遇到问题：{str(e)}", thought_log
    else:
        yield "亲爱的游客，请告诉我您想去的城市，我也好为您规划呀！", thought_log

# ================= 4. UI 界面 =================
with gr.Blocks(title="多智能体旅行规划专家") as demo:
    gr.Markdown("# 🌍 一站式智能旅行规划专家 (Multi-Agent 系统)")
    
    with gr.Row():
        with gr.Column(scale=4):
            chatbot = gr.Chatbot(label="Agent 集群对话中", height=650)
            msg = gr.Textbox(placeholder="帮我规划成都攻略 / 帮我归档", label="您的旅行指令")
            thought_display = gr.HighlightedText(label="Agent 协作链路日志")
            with gr.Row():
                clear = gr.Button("🗑️ 清空历史")
                submit = gr.Button("🚀 立即执行", variant="primary")
        with gr.Column(scale=1):
            gr.Markdown("### 🤖 节点状态")
            gr.Label(value="Agent 1: 规划专家 (Active)", label="状态")
            gr.Label(value="Agent 2: 归档专家 (Active)", label="状态")
            gr.Markdown("""
            **操作说明：**
            1. 正常提问获取旅游规划。
            2. **重点**：看到满意的攻略后，紧接着输入“**帮我归档**”即可存入本地 `saved_plans`。
            """)

    def chat_wrapper(message, chat_history):
        chat_history.append((message, ""))
        for bot_res, log in agent_predict(message, chat_history):
            chat_history[-1] = (message, bot_res)
            formatted_log = [(l, l[0]) for l in log]
            yield chat_history, formatted_log

    submit.click(chat_wrapper, [msg, chatbot], [chatbot, thought_display])
    msg.submit(chat_wrapper, [msg, chatbot], [chatbot, thought_display])
    clear.click(lambda: ([], []), None, [chatbot, thought_display])

if __name__ == "__main__":
    # 使用 6008 端口启动
    demo.queue().launch(server_name="0.0.0.0", server_port=6008, share=True)