# 示例：加载模型
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
model = PeftModel.from_pretrained(base_model, "./output/checkpoint-500") # 你的微调结果

class TravelAgent:
    def __init__(self, model_path):
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
        print(f"正在加载微调后的模型: {model_path}")

    def run(self, user_input):
        # 这里模拟 ReAct 过程
        # 1. 识别意图 -> 2. 调用 tools_dict -> 3. 整理回答
        print(f"用户问题: {user_input}")
        return "亲爱的游客，我已经为您查好了！上海明天天气晴朗，从外滩去豫园不远，建议您打车..."

if __name__ == "__main__":
    agent = TravelAgent("./output/checkpoint-500")
    print(agent.run("我想去上海玩，帮我规划路线"))