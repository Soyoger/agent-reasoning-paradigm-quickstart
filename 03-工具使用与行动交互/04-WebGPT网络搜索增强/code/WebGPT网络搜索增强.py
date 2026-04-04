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

# Wikipedia API 配置
search_url = "https://zh.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&format=json"

# 添加 User-Agent 头部以避免被网站阻止
headers = {
    "User-Agent": "https://w.wiki/4wJS (4wJS)"
}

def search_wikipedia(query: str) -> list:
    """搜索维基百科并返回结果列表"""
    try:
        response = requests.get(search_url.format(query), headers=headers)
        response.raise_for_status()
        data = response.json()

        results = []
        if data and "query" in data and "search" in data["query"]:
            # 限制返回前3个结果
            for i, item in enumerate(data["query"]["search"]):
                if i >= 3:
                    break
                results.append({
                    "title": item["title"],
                    "snippet": item["snippet"]
                })
        return results
    except Exception as e:
        print(f"搜索出错: {e}")
        return []

def get_web_page_content(title: str) -> str:
    """获取维基百科页面内容"""
    try:
        # 使用 Wikipedia API 获取页面内容
        import urllib.parse
        encoded_title = urllib.parse.quote(title)
        url = f"https://zh.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "extract" in data:
            return data["extract"]
        else:
            return f"无法获取'{title}'的详细内容。"
    except Exception as e:
        print(f"获取页面内容出错: {e}")
        return f"获取'{title}'的内容时发生错误。"

class MockBrowser:
    def __init__(self):
        self.current_page = None
        self.history = []

    def search(self, query: str) -> list:
        # 使用真实 Wikipedia API 替代模拟数据
        return search_wikipedia(query)

    def navigate(self, title: str) -> str:
        self.current_page = title
        self.history.append(title)
        # 使用真实内容获取替代模拟数据
        return get_web_page_content(title)

    def get_current_page(self) -> str:
        if self.current_page:
            return get_web_page_content(self.current_page)
        return ""


def get_tools():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search",
                "description": "搜索关键词，返回搜索结果列表",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "navigate",
                "description": "打开搜索结果中的某个网页",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "网页标题"}
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "answer_with_quote",
                "description": "根据浏览的网页内容，给出带引用的答案",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string", "description": "最终答案"},
                        "quotes": {"type": "array", "items": {"type": "string"}, "description": "引用的网页内容列表"}
                    },
                    "required": ["answer", "quotes"]
                }
            }
        }
    ]
    return tools


def webgpt_loop(question: str, max_steps: int = 5):
    print("=" * 60)
    print(f"【WebGPT 模拟】问题：{question}")
    print("=" * 60)

    browser = MockBrowser()
    messages = [
        {"role": "system", "content": """你是WebGPT，一个可以搜索和浏览网页的助手。
你可以使用以下工具：
1. search(query): 搜索关键词
2. navigate(title): 打开网页
3. answer_with_quote(answer, quotes): 给出带引用的答案

流程建议：先搜索，再浏览相关网页，最后用answer_with_quote给出答案。"""},
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
            print(f">>> 输出：{message.content}")
            continue

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            print(f">>> 调用工具：{tool_name}({json.dumps(tool_args, ensure_ascii=False)})")

            tool_result = ""
            if tool_name == "search":
                results = browser.search(tool_args["query"])
                tool_result = json.dumps(results, ensure_ascii=False)
                print(f">>> 搜索结果：{tool_result}")
            elif tool_name == "navigate":
                content = browser.navigate(tool_args["title"])
                tool_result = content
                print(f">>> 网页内容：{content}")
            elif tool_name == "answer_with_quote":
                print(f">>> 最终答案：{tool_args['answer']}")
                print(f">>> 引用：")
                for i, q in enumerate(tool_args['quotes'], 1):
                    print(f"  [{i}] {q}")
                print("\n" + "=" * 60)
                return

            tool_response = {
                "role": "tool",
                "content": tool_result,
                "tool_call_id": tool_call.id
            }
            messages.append(tool_response)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    webgpt_loop("特斯拉是什么？", max_steps=5)
