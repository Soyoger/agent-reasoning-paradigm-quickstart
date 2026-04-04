import json
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)


@dataclass
class PlanStep:
    id: int
    name: str
    tool: str
    params: Dict[str, Any]
    status: str = "pending"
    output: str = ""
    error: str = ""


def weather_tool(city: str) -> str:
    weather = {
        "上海": "中雨, 18°C",
        "北京": "晴, 24°C",
        "深圳": "多云, 28°C"
    }
    return weather.get(city, "未知天气")


def traffic_tool(origin: str, destination: str) -> str:
    if origin == "陆家嘴" and destination == "虹桥":
        return "重度拥堵"
    return "中度拥堵"


def eta_tool(distance_km: float, congestion: str, weather: str) -> str:
    base_speed = 45.0
    if "重度拥堵" in congestion:
        base_speed = 22.0
    elif "中度拥堵" in congestion:
        base_speed = 30.0
    if "雨" in weather:
        base_speed *= 0.85
    eta_minutes = int((distance_km / base_speed) * 60)
    return f"{eta_minutes}分钟"


def create_fallback_plan(question: str) -> Dict[str, Any]:
    return {
        "goal": question,
        "steps": [
            {
                "id": 1,
                "name": "查询天气",
                "tool": "weather_tool",
                "params": {"city": "上海"}
            },
            {
                "id": 2,
                "name": "查询路况",
                "tool": "traffic_tool",
                "params": {"origin": "陆家嘴", "destination": "虹桥"}
            },
            {
                "id": 3,
                "name": "估算到达时间",
                "tool": "eta_tool",
                "params": {"distance_km": 22}
            }
        ]
    }


def build_plan(question: str) -> Dict[str, Any]:
    prompt = f"""你是任务规划器。请把用户问题拆解为3-5个可执行步骤，仅输出JSON。
字段要求：
- goal: 任务目标
- steps: 数组，每项包含 id, name, tool, params
可选工具：weather_tool, traffic_tool, eta_tool
用户问题：{question}
"""
    try:
        resp = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            stream=False
        )
        text = resp.choices[0].message.content.strip()
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
    except Exception:
        pass
    return create_fallback_plan(question)


def execute_step(step: PlanStep, context: Dict[str, Any]) -> PlanStep:
    try:
        if step.tool == "weather_tool":
            city = step.params.get("city", "上海")
            result = weather_tool(city)
            context["weather"] = result
        elif step.tool == "traffic_tool":
            origin = step.params.get("origin", "陆家嘴")
            destination = step.params.get("destination", "虹桥")
            result = traffic_tool(origin, destination)
            context["traffic"] = result
        elif step.tool == "eta_tool":
            distance_km = float(step.params.get("distance_km", 20))
            traffic = context.get("traffic", "中度拥堵")
            weather = context.get("weather", "多云")
            result = eta_tool(distance_km, traffic, weather)
            context["eta"] = result
        else:
            raise ValueError(f"未知工具: {step.tool}")
        step.status = "done"
        step.output = result
    except Exception as e:
        step.status = "failed"
        step.error = str(e)
    return step


def execute_plan(plan: Dict[str, Any], max_retries: int = 2) -> Dict[str, Any]:
    context: Dict[str, Any] = {}
    executed_steps: List[PlanStep] = []
    for raw in plan.get("steps", []):
        step = PlanStep(
            id=int(raw.get("id", len(executed_steps) + 1)),
            name=str(raw.get("name", f"步骤{len(executed_steps)+1}")),
            tool=str(raw.get("tool", "")),
            params=dict(raw.get("params", {}))
        )
        retries = 0
        while retries < max_retries:
            step = execute_step(step, context)
            if step.status == "done":
                break
            retries += 1
            time.sleep(0.1)
        executed_steps.append(step)
    return {
        "goal": plan.get("goal", ""),
        "steps": [asdict(s) for s in executed_steps],
        "context": context
    }


def summarize_result(execution_result: Dict[str, Any]) -> str:
    weather = execution_result.get("context", {}).get("weather", "未知")
    traffic = execution_result.get("context", {}).get("traffic", "未知")
    eta = execution_result.get("context", {}).get("eta", "未知")
    if "重度拥堵" in traffic:
        return f"当前天气{weather}，路况{traffic}，预计{eta}。建议优先绕行。"
    return f"当前天气{weather}，路况{traffic}，预计{eta}。建议按常规路线行驶。"


def plan_and_execute(question: str):
    print("=" * 60)
    print(f"【任务】{question}")
    print("=" * 60)
    start = time.time()
    plan = build_plan(question)
    print("\n【计划】")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    result = execute_plan(plan, max_retries=2)
    print("\n【执行轨迹】")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    answer = summarize_result(result)
    print("\n【最终建议】")
    print(answer)
    elapsed = time.time() - start
    print(f"\n【总耗时】{elapsed:.2f}s")


if __name__ == "__main__":
    question = "请给出今天下班从陆家嘴到虹桥的出行建议，考虑天气和路况。"
    plan_and_execute(question)
