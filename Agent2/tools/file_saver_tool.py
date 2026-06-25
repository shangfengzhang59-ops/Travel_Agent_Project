import os
import datetime

def save_travel_plan(content: str, city: str, **kwargs):
    """
    将生成的旅行规划保存为本地 Markdown 文件。
    :param content: 攻略内容
    :param city: 城市名称
    """
    # 1. 确定保存路径
    base_dir = "/root/autodl-tmp/Travel_Agent_Project/saved_plans"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # 2. 生成文件名：城市_时间戳.md
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{city}_{timestamp}.md"
    file_path = os.path.join(base_dir, filename)

    # 3. 写入文件
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {city} 旅行规划档案\n")
            f.write(f"> 归档时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(content)
        return f"【归档成功】文件已保存至：{file_path}"
    except Exception as e:
        return f"【归档失败】错误原因：{str(e)}"

# 暴露工具字典
AGENT2_TOOLS = {
    "save_travel_plan": save_travel_plan
}