import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

KNOWLEDGE_BASE = {
    "特斯拉": "特斯拉（Tesla, Inc.）是一家美国电动汽车和能源公司，成立于2003年。",
    "特斯拉成立时间": "特斯拉成立于2003年。",
    "Model 3": "特斯拉Model 3是一款紧凑型电动轿车，2017年开始量产。",
    "比亚迪": "比亚迪股份有限公司是一家中国新能源汽车和电池制造商，成立于1995年。"
}


def search_wikipedia(query: str) -> str:
    for key, value in KNOWLEDGE_BASE.items():
        if key in query:
            return value
    return f"未找到关于'{query}'的详细信息。"


def calculator(expr: str) -> str:
    try:
        result = eval(expr)
        return str(result)
    except:
        return "计算错误"


def get_tools():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_wikipedia",
                "description": "搜索维基百科获取事实信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "要搜索的关键词"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "计算数学表达式",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expr": {
                            "type": "string",
                            "description": "数学表达式，如 '2*3+5'"
                        }
                    },
                    "required": ["expr"]
                }
            }
        }
    ]
    return tools


def execute_tool(tool_name: str, tool_args: dict) -> str:
    if tool_name == "search_wikipedia":
        return search_wikipedia(tool_args.get("query", ""))
    elif tool_name == "calculator":
        return calculator(tool_args.get("expr", ""))
    else:
        return f"未知工具：{tool_name}"


def function_calling_loop(question: str, max_steps: int = 5):
    print("=" * 60)
    print(f"【Function Calling 示例】问题：{question}")
    print("=" * 60)

    messages = [
        {"role": "system", "content": "你是一个专业的助手，可以使用工具来回答问题。"},
        {"role": "user", "content": question}
    ]

    count = 0
    while count < max_steps:
        count += 1
        print(f"\n【步骤 {count}】")

        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2",
            messages=messages,
            tools=get_tools(),
            tool_choice="auto",
            stream=False,
            temperature=0.3
        )

        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            print(f">>> 最终答案：{message.content}")
            break

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            print(f">>> 调用工具：{tool_name}({json.dumps(tool_args, ensure_ascii=False)})")

            tool_result = execute_tool(tool_name, tool_args)
            print(f">>> 工具返回：{tool_result}")

            tool_response = {
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tool_call.id
            }
            messages.append(tool_response)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    questions = [
        "特斯拉是哪一年成立的？",
        "2*3+5等于多少？"
    ]

    for q in questions:
        print("\n" + "=" * 60)
        function_calling_loop(q)
