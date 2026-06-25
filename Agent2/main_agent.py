import os
import datetime

def archivist_agent_logic(content, city):
    """
    Agent 2 的核心功能：将攻略存入本地
    """
    # 1. 确定保存目录
    save_dir = "/root/autodl-tmp/Travel_Agent_Project/saved_plans"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 2. 生成文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # 过滤掉文件名中可能非法字符
    safe_city = city.strip().replace("/", "_")
    filename = f"{safe_city}_旅行攻略_{timestamp}.md"
    file_path = os.path.join(save_dir, filename)
    
    # 3. 写入内容
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {city} 旅行规划档案\n")
            f.write(f"> 归档时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(content)
        return f"已成功归档至本地：{file_path}"
    except Exception as e:
        return f"归档过程中发生错误：{str(e)}"
