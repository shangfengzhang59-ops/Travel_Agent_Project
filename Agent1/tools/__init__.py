from .weather_tool import get_weather
from .map_tool import get_map_route
from .search_tool import search_attractions

TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "get_map_route": get_map_route,
    "search_attractions": search_attractions
}
