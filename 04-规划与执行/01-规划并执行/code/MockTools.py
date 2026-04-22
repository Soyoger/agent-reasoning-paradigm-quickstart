from typing import List, Dict

def get_mock_tools() -> List[Dict]:
    """
    通用Mock工具定义（共50个，涵盖衣食住行、百科、天气、物理常识）
    """
    return [
        # === 衣 (5个) ===
        {"type": "function", "function": {"name": "get_clothing_advice", "description": "根据天气和场合给出服装建议", "parameters": {"type": "object", "properties": {"weather": {"type": "string"}, "occasion": {"type": "string"}}, "required": ["weather"]}}},
        {"type": "function", "function": {"name": "get_size_guide", "description": "提供服装尺码选择指南", "parameters": {"type": "object", "properties": {"brand": {"type": "string"}, "category": {"type": "string"}}, "required": ["brand"]}}},
        {"type": "function", "function": {"name": "get_wash_instruction", "description": "获取服装洗涤说明", "parameters": {"type": "object", "properties": {"fabric": {"type": "string"}}, "required": ["fabric"]}}},
        {"type": "function", "function": {"name": "match_colors", "description": "提供颜色搭配建议", "parameters": {"type": "object", "properties": {"base_color": {"type": "string"}, "style": {"type": "string"}}, "required": ["base_color"]}}},
        {"type": "function", "function": {"name": "get_seasonal_style", "description": "获取季节性穿搭推荐", "parameters": {"type": "object", "properties": {"season": {"type": "string"}, "region": {"type": "string"}}, "required": ["season"]}}},

        # === 食 (10个) ===
        {"type": "function", "function": {"name": "search_recipe", "description": "搜索食谱和烹饪方法", "parameters": {"type": "object", "properties": {"ingredient": {"type": "string"}}, "required": ["ingredient"]}}},
        {"type": "function", "function": {"name": "get_nutrition_info", "description": "获取食物营养成分", "parameters": {"type": "object", "properties": {"food": {"type": "string"}}, "required": ["food"]}}},
        {"type": "function", "function": {"name": "find_restaurant", "description": "查找附近餐厅", "parameters": {"type": "object", "properties": {"cuisine": {"type": "string"}, "location": {"type": "string"}}, "required": ["cuisine"]}}},
        {"type": "function", "function": {"name": "check_food_expiry", "description": "检查食品保质期", "parameters": {"type": "object", "properties": {"food": {"type": "string"}}, "required": ["food"]}}},
        {"type": "function", "function": {"name": "get_diet_plan", "description": "生成饮食计划", "parameters": {"type": "object", "properties": {"goal": {"type": "string"}, "calories": {"type": "number"}}, "required": ["goal"]}}},
        {"type": "function", "function": {"name": "check_allergen", "description": "检查食物过敏原", "parameters": {"type": "object", "properties": {"dish": {"type": "string"}}, "required": ["dish"]}}},
        {"type": "function", "function": {"name": "get_cooking_tips", "description": "获取烹饪技巧", "parameters": {"type": "object", "properties": {"technique": {"type": "string"}}, "required": ["technique"]}}},
        {"type": "function", "function": {"name": "find_wine_pairing", "description": "查找酒类搭配", "parameters": {"type": "object", "properties": {"food": {"type": "string"}}, "required": ["food"]}}},
        {"type": "function", "function": {"name": "get_hangover_cure", "description": "获取解酒方法", "parameters": {"type": "object", "properties": {"severity": {"type": "string"}}, "required": ["severity"]}}},
        {"type": "function", "function": {"name": "get_calorie_count", "description": "计算食物卡路里", "parameters": {"type": "object", "properties": {"food": {"type": "string"}, "grams": {"type": "number"}}, "required": ["food"]}}},

        # === 住 (10个) ===
        {"type": "function", "function": {"name": "search_real_estate", "description": "搜索房产信息", "parameters": {"type": "object", "properties": {"city": {"type": "string"}, "budget": {"type": "string"}}, "required": ["city"]}}},
        {"type": "function", "function": {"name": "get_rent_estimate", "description": "估算租金", "parameters": {"type": "object", "properties": {"area": {"type": "number"}, "location": {"type": "string"}}, "required": ["area"]}}},
        {"type": "function", "function": {"name": "get_neighborhood_info", "description": "获取社区信息", "parameters": {"type": "object", "properties": {"district": {"type": "string"}}, "required": ["district"]}}},
        {"type": "function", "function": {"name": "check_furniture_assembly", "description": "提供家具组装说明", "parameters": {"type": "object", "properties": {"furniture": {"type": "string"}}, "required": ["furniture"]}}},
        {"type": "function", "function": {"name": "get_appliance_manual", "description": "获取家电使用手册", "parameters": {"type": "object", "properties": {"appliance": {"type": "string"}}, "required": ["appliance"]}}},
        {"type": "function", "function": {"name": "calculate_mortgage", "description": "计算房贷月供", "parameters": {"type": "object", "properties": {"principal": {"type": "number"}, "rate": {"type": "number"}, "years": {"type": "number"}}, "required": ["principal"]}}},
        {"type": "function", "function": {"name": "get_home_insurance", "description": "获取家财险信息", "parameters": {"type": "object", "properties": {"value": {"type": "number"}}, "required": ["value"]}}},
        {"type": "function", "function": {"name": "find_property_agent", "description": "查找房产经纪人", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
        {"type": "function", "function": {"name": "check_noise_level", "description": "检查噪音水平", "parameters": {"type": "object", "properties": {"address": {"type": "string"}}, "required": ["address"]}}},
        {"type": "function", "function": {"name": "estimate_utilities", "description": "估算水电煤费用", "parameters": {"type": "object", "properties": {"area": {"type": "number"}, "people": {"type": "number"}}, "required": ["area"]}}},

        # === 行 (10个) ===
        {"type": "function", "function": {"name": "get_traffic_route", "description": "规划出行路线", "parameters": {"type": "object", "properties": {"origin": {"type": "string"}, "destination": {"type": "string"}}, "required": ["origin", "destination"]}}},
        {"type": "function", "function": {"name": "get_eta", "description": "估算到达时间", "parameters": {"type": "object", "properties": {"distance": {"type": "number"}, "traffic": {"type": "string"}}, "required": ["distance"]}}},
        {"type": "function", "function": {"name": "find_nearby_station", "description": "查找附近站点", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}},
        {"type": "function", "function": {"name": "get_bus_schedule", "description": "获取公交时刻表", "parameters": {"type": "object", "properties": {"line": {"type": "string"}}, "required": ["line"]}}},
        {"type": "function", "function": {"name": "get_flight_status", "description": "查询航班状态", "parameters": {"type": "object", "properties": {"flight": {"type": "string"}}, "required": ["flight"]}}},
        {"type": "function", "function": {"name": "get_train_schedule", "description": "查询火车时刻表", "parameters": {"type": "object", "properties": {"from_station": {"type": "string"}, "to_station": {"type": "string"}}, "required": ["from_station"]}}},
        {"type": "function", "function": {"name": "calculate_trip_cost", "description": "计算出行费用", "parameters": {"type": "object", "properties": {"distance": {"type": "number"}, "mode": {"type": "string"}}, "required": ["distance"]}}},
        {"type": "function", "function": {"name": "get_parking_info", "description": "获取停车场信息", "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}},
        {"type": "function", "function": {"name": "get_traffic_camera", "description": "查询路况摄像头", "parameters": {"type": "object", "properties": {"highway": {"type": "string"}}, "required": ["highway"]}}},
        {"type": "function", "function": {"name": "get_traffic_rules", "description": "获取交通规则", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},

        # === 百科 (10个) ===
        {"type": "function", "function": {"name": "search_wikipedia", "description": "搜索维基百科", "parameters": {"type": "object", "properties": {"topic": {"type": "string"}}, "required": ["topic"]}}},
        {"type": "function", "function": {"name": "get_knowledge", "description": "获取通用知识", "parameters": {"type": "object", "properties": {"category": {"type": "string"}}, "required": ["category"]}}},
        {"type": "function", "function": {"name": "get_history_event", "description": "获取历史事件", "parameters": {"type": "object", "properties": {"year": {"type": "string"}}, "required": ["year"]}}},
        {"type": "function", "function": {"name": "get_celebrity_bio", "description": "获取名人传记", "parameters": {"type": "object", "properties": {"person": {"type": "string"}}, "required": ["person"]}}},
        {"type": "function", "function": {"name": "get_science_fact", "description": "获取科学知识", "parameters": {"type": "object", "properties": {"field": {"type": "string"}}, "required": ["field"]}}},
        {"type": "function", "function": {"name": "solve_math", "description": "数学题解答", "parameters": {"type": "object", "properties": {"problem": {"type": "string"}}, "required": ["problem"]}}},
        {"type": "function", "function": {"name": "translate_text", "description": "翻译文本", "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "target_lang": {"type": "string"}}, "required": ["text"]}}},
        {"type": "function", "function": {"name": "get_word_definition", "description": "获取词义解释", "parameters": {"type": "object", "properties": {"word": {"type": "string"}}, "required": ["word"]}}},
        {"type": "function", "function": {"name": "get_synonyms", "description": "获取同义词", "parameters": {"type": "object", "properties": {"word": {"type": "string"}}, "required": ["word"]}}},
        {"type": "function", "function": {"name": "get_antonyms", "description": "获取反义词", "parameters": {"type": "object", "properties": {"word": {"type": "string"}}, "required": ["word"]}}},

        # === 天气 (5个) ===
        {"type": "function", "function": {"name": "get_weather", "description": "查询天气", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
        {"type": "function", "function": {"name": "get_forecast", "description": "获取天气预报", "parameters": {"type": "object", "properties": {"city": {"type": "string"}, "days": {"type": "number"}}, "required": ["city"]}}},
        {"type": "function", "function": {"name": "get_air_quality", "description": "查询空气质量", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
        {"type": "function", "function": {"name": "get_uv_index", "description": "查询紫外线指数", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},
        {"type": "function", "function": {"name": "get_weather_alert", "description": "获取天气预警", "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}},

        # === 物理 (5个) ===
        {"type": "function", "function": {"name": "calc_distance", "description": "计算两点距离", "parameters": {"type": "object", "properties": {"from_loc": {"type": "string"}, "to_loc": {"type": "string"}}, "required": ["from_loc"]}}},
        {"type": "function", "function": {"name": "calc_speed", "description": "计算速度", "parameters": {"type": "object", "properties": {"distance": {"type": "number"}, "time": {"type": "number"}}, "required": ["distance"]}}},
        {"type": "function", "function": {"name": "convert_units", "description": "单位换算", "parameters": {"type": "object", "properties": {"value": {"type": "number"}, "from_unit": {"type": "string"}, "to_unit": {"type": "string"}}, "required": ["value"]}}},
        {"type": "function", "function": {"name": "calc_area", "description": "计算面积", "parameters": {"type": "object", "properties": {"length": {"type": "number"}, "width": {"type": "number"}}, "required": ["length"]}}},
        {"type": "function", "function": {"name": "calc_volume", "description": "计算体积", "parameters": {"type": "object", "properties": {"length": {"type": "number"}, "width": {"type": "number"}, "height": {"type": "number"}}, "required": ["length"]}}},
    ]


def execute_mock_tool(tool_name: str, arguments: Dict) -> str:
    """执行Mock工具"""
    handlers = {
        # 衣
        "get_clothing_advice": lambda a: f"建议{a.get('weather','晴天')}场合穿着{a.get('occasion','')}",
        "get_size_guide": lambda a: f"{a.get('brand')}品牌{a.get('category')}尺码参考",
        "get_wash_instruction": lambda a: f"{a.get('fabric')}洗涤说明",
        "match_colors": lambda a: f"{a.get('base_color')}搭配建议",
        "get_seasonal_style": lambda a: f"{a.get('season')}季节穿搭推荐",
        # 食
        "search_recipe": lambda a: f"{a.get('ingredient')}家常做法",
        "get_nutrition_info": lambda a: f"{a.get('food')}营养成分",
        "find_restaurant": lambda a: f"{a.get('location')}附近{a.get('cuisine')}餐厅",
        "check_food_expiry": lambda a: f"{a.get('food')}保质期检查",
        "get_diet_plan": lambda a: f"每日{a.get('calories',2000)}大卡饮食计划",
        "check_allergen": lambda a: f"{a.get('dish')}过敏原检查",
        "get_cooking_tips": lambda a: f"{a.get('technique')}技巧",
        "find_wine_pairing": lambda a: f"{a.get('food')}酒搭配建议",
        "get_hangover_cure": lambda a: f"解酒方法",
        "get_calorie_count": lambda a: f"{a.get('food')}{a.get('grams',100)}g卡路里计算",
        # 住
        "search_real_estate": lambda a: f"{a.get('city')}房产信息",
        "get_rent_estimate": lambda a: f"面积{a.get('area')}平米租金估算",
        "get_neighborhood_info": lambda a: f"{a.get('district')}社区信息",
        "check_furniture_assembly": lambda a: f"{a.get('furniture')}组装说明",
        "get_appliance_manual": lambda a: f"{a.get('appliance')}使用手册",
        "calculate_mortgage": lambda a: f"房贷{a.get('principal')}元计算",
        "get_home_insurance": lambda a: f"家财险{a.get('value')}元",
        "find_property_agent": lambda a: f"{a.get('city')}房产经纪人",
        "check_noise_level": lambda a: f"{a.get('address')}噪音检查",
        "estimate_utilities": lambda a: f"水电煤费用估算",
        # 行
        "get_traffic_route": lambda a: f"从{a.get('origin')}到{a.get('destination')}路线",
        "get_eta": lambda a: f"预计{a.get('distance')}公里耗时",
        "find_nearby_station": lambda a: f"附近{a.get('location')}站点",
        "get_bus_schedule": lambda a: f"{a.get('line')}路公交时刻",
        "get_flight_status": lambda a: f"航班{a.get('flight')}状态",
        "get_train_schedule": lambda a: f"火车{a.get('fromStation')}到{a.get('toStation')}",
        "calculate_trip_cost": lambda a: f"出行费用{a.get('distance')}公里",
        "get_parking_info": lambda a: f"{a.get('location')}停车场",
        "get_traffic_camera": lambda a: f"{a.get('highway')}路况",
        "get_traffic_rules": lambda a: f"{a.get('city')}交通规则",
        # 百科
        "search_wikipedia": lambda a: f"关于{a.get('topic')}的百科",
        "get_knowledge": lambda a: f"{a.get('category')}知识",
        "get_history_event": lambda a: f"{a.get('year')}年历史事件",
        "get_celebrity_bio": lambda a: f"{a.get('person')}传记",
        "get_science_fact": lambda a: f"{a.get('field')}科学知识",
        "solve_math": lambda a: f"解答：{a.get('problem')}",
        "translate_text": lambda a: f"翻译：{a.get('text')}",
        "get_word_definition": lambda a: f"词汇定义",
        "get_synonyms": lambda a: f"同义词列表",
        "get_antonyms": lambda a: f"反义词列表",
        # 天气
        "get_weather": lambda a: f"{a.get('city')}天气",
        "get_forecast": lambda a: f"{a.get('city')}天气预报",
        "get_air_quality": lambda a: f"{a.get('city')}空气质量",
        "get_uv_index": lambda a: f"{a.get('city')}紫外线",
        "get_weather_alert": lambda a: f"{a.get('city')}天气预警",
        # 物理
        "calc_distance": lambda a: f"距离计算",
        "calc_speed": lambda a: f"速度：{a.get('distance')/max(a.get('time',1),1)}",
        "convert_units": lambda a: f"单位换算",
        "calc_area": lambda a: f"面积：{a.get('length')*a.get('width',1)}",
        "calc_volume": lambda a: f"体积：{a.get('length')*a.get('width',1)*a.get('height',1)}",
    }
    return handlers.get(tool_name, lambda _: f"未知工具: {tool_name}")(arguments)

if __name__ == "__main__":
    tools = get_mock_tools()
    print(f"工具总数: {len(tools)}")
    for t in tools:
        print(f"  - {t['function']['name']}")