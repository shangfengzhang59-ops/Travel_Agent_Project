import requests

def get_location_coordinate(location_name, key):
    """将地名转换为经纬度"""
    url = f"https://restapi.amap.com/v3/geocode/geo?address={location_name}&key={key}"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if data["status"] == "1" and len(data["geocodes"]) > 0:
            return data["geocodes"][0]["location"]
    except:
        return None
    return None

def get_map_route(origin=None, destination=None, **kwargs):
    """
    路径规划工具
    :param origin: 起点名称
    :param destination: 终点名称
    :param kwargs: 接收如 city, date 等模型乱传的参数
    """
    key = "298991381ae5a85817b67f762e879f58" # ⬅️ 务必修改此处
    
    # 参数补全逻辑：如果模型只传了 city
    city = kwargs.get("city", "成都")
    if not origin: origin = f"{city}站"
    if not destination: destination = f"{city}中心"

    # 1. 转换坐标
    origin_coord = get_location_coordinate(origin, key)
    dest_coord = get_location_coordinate(destination, key)
    
    if not origin_coord or not dest_coord:
        return f"【地图】抱歉，无法定位 '{origin}' 或 '{destination}'。请检查地名是否准确。"

    # 2. 调用步行路径规划
    url = f"https://restapi.amap.com/v3/direction/walking?origin={origin_coord}&destination={dest_coord}&key={key}"
    
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if data["status"] == "1":
            path = data["route"]["paths"][0]
            dist = int(path["distance"])
            dur = int(path["duration"])
            return (f"从{origin}到{destination}全程约 {dist/1000:.2f}公里，"
                    f"预计步行耗时 {dur//60}分钟。建议穿舒适的鞋子。")
        return "【地图】路径规划暂时失败。"
    except:
        return "【地图】API 连接超时。"