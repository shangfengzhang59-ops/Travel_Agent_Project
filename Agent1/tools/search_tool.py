import requests

def search_attractions(city: str, keywords: str):
    """
    接入 SerpApi 获取实时旅游资讯
    """
    # 1. 配置你的 API Key
    api_key = "e862287f9e50905b2889dcd35484382bbf90559d074542628b435e0f847bc7b9"
    
    # 2. 优化搜索关键词：强制让它搜索“小红书”或“攻略”相关内容
    search_query = f"{city} {keywords} 旅游攻略 2024 建议"
    
    # 3. 构建请求参数
    # engine=google：使用谷歌引擎效果最好
    # hl=zh-cn：强制返回中文结果
    url = f"https://serpapi.com/search"
    params = {
        "q": search_query,
        "api_key": api_key,
        "engine": "google",
        "hl": "zh-cn",
        "gl": "cn" # 搜索地区设定为中国
    }
    
    try:
        # 发起请求
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # 4. 提取搜索结果摘要 (Snippets)
        # 我们不仅提取普通结果，还尝试提取“知识卡片”或“置顶回答”
        results = data.get("organic_results", [])
        
        if not results:
            return f"【搜索系统】在网上没有找到关于{city}{keywords}的具体建议，可能是关键词太生僻了。"

        # 组合前 4 条结果，形成一个丰富的“素材池”
        content_snippets = []
        for i, res in enumerate(results[:4]):
            title = res.get('title', '')
            snippet = res.get('snippet', '')
            content_snippets.append(f"素材{i+1} [{title}]: {snippet}")
            
        context = "\n".join(content_snippets)
        
        # 5. 返回结构化素材，方便 Agent 后续撰写长文
        return f"【实时互联网资讯检索结果】:\n{context}"

    except Exception as e:
        # 降级方案：如果 API 出错（如欠费或网络问题），返回详细的 Mock 数据
        return f"【系统提示】实时搜索暂时不可用，但根据我的本地知识库，{city}的{keywords}推荐：前往热门步行街，并尝试当地老字号餐厅。"