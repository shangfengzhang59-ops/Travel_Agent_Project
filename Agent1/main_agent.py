import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tools import TOOL_FUNCTIONS

# 1. 加载模型 (指向你 AutoDL 上的路径)
model_path = "/root/autodl-tmp/Qwen2.5-0.5B-Instruct" # 确保路径正确
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")

def run_agent(user_query):
    # 构建 Prompt，告诉模型你有这些工具
# 优化后的 Prompt 模板
    prompt = f"""<|im_start|>system
    你是一个专业的金牌导游。你必须严格按下述格式回答。

    你可以调用：
    1. get_weather(city): 获取天气。
    2. get_map_route(origin, destination): 规划路线。

    [例子]
    用户问：北京天气。
    思考：需要查天气。
    Action: get_weather, Args: {{"city": "北京"}}

    用户问：你好。
    思考：这是打招呼。
    回答：亲爱的游客，您好！我是您的旅行管家。
    <|im_end|>
    <|im_start|>user
    {user_query}
    <|im_end|>
    <|im_start|>assistant
    思考："""
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=100)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print(f"--- 模型思考中 ---\n{response}")
    
    # 解析模型输出并执行工具 (简单逻辑示例)
    if "get_weather" in response:
        # 这里建议用正则表达式提取参数，先手动模拟一下逻辑
        result = TOOL_FUNCTIONS['get_weather'](city="北京")
        print(f"--- 工具执行结果 ---\n{result}")
        return result
    else:
        return response

if __name__ == "__main__":
    query = "帮我看看北京的天气怎么样？"
    final_res = run_agent(query)
    print(f"--- 最终回答 ---\n{final_res}")