import sys
import json
import requests
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

system_prompt = """
你是一个专业的助手，能够使用工具来回答问题。
当你需要信息时，请使用Search工具搜索维基百科。
"""

search_url = "https://zh.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&format=json"

# b'Please set a user-agent and respect our robot policy https://w.wiki/4wJS. See also https://phabricator.wikimedia.org/T400119.\n'
headers = {
    "User-Agent": "https://w.wiki/4wJS (4wJS)"
}
def search_wikipedia(query: str) -> str:
    response = requests.get(search_url.format(query), headers=headers)
    data = response.json()
    if data and len(data["query"]["search"]) > 0:
        title = data["query"]["search"][0]["title"]
        summary = data["query"]["search"][0]["snippet"]
        return f"{title}\n{summary}"
    else:
        return f"未找到关于'{query}'的详细信息。"


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
                            "description": "要搜索的维基百科查询"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    return tools


def react_loop(question: str, max_steps: int = 5):
    messages = [
        {"role": "system", "content": system_prompt},
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
            print(f">>> 最终答案: {message.content}")
            break

        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        query = tool_args.get("query", "")
        print(f">>> 调用工具: {tool_name}('{query}')")

        tool_result = search_wikipedia(query)
        print(f">>> 工具返回: {tool_result}")

        tool_response_message = {
            "role": "tool",
            "name": tool_name,
            "content": tool_result,
            "tool_call_id": tool_call.id
        }
        messages.append(tool_response_message)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    react_loop("特斯拉的百科？", max_steps=5)
