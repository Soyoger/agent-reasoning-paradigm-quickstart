import sys
import re
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


def parse_api_calls(text: str) -> list:
    pattern = r'\[(\w+)\((.*?)\)\]'
    matches = re.findall(pattern, text)
    return matches


def toolformer_inference(question: str) -> str:
    print("=" * 60)
    print(f"【ToolFormer 模拟】问题：{question}")
    print("=" * 60)

    system_prompt = """你是一个助手，当你需要信息或计算时，可以使用工具。
    工具调用格式：[工具名(参数)]
    可用工具：
    - Search(query): 搜索维基百科
    - Calculator(expr): 计算数学表达式

    示例：
    用户：特斯拉成立于哪一年？
    你：特斯拉成立于[Search(特斯拉成立时间)]。
    （执行工具后）
    你：特斯拉成立于2003年。

    用户：2*3+5等于多少？
    你：2*3+5等于[Calculator(2*3+5)]。
    （执行工具后）
    你：2*3+5等于11。
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    max_rounds = 3
    for round_idx in range(max_rounds):
        print(f"\n【轮次 {round_idx + 1}】")

        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2",
            messages=messages,
            stream=False,
            temperature=0.3
        )

        output = response.choices[0].message.content.strip()
        print(f">>> 输出：{output}")

        api_calls = parse_api_calls(output)

        if not api_calls:
            print("\n" + "=" * 60)
            print(f">>> 最终答案：{output}")
            print("=" * 60)
            return output

        tool_name, tool_arg = api_calls[0]
        print(f">>> 检测到工具调用：{tool_name}('{tool_arg}')")

        if tool_name == "Search":
            tool_result = search_wikipedia(tool_arg)
        elif tool_name == "Calculator":
            tool_result = calculator(tool_arg)
        else:
            tool_result = f"未知工具：{tool_name}"

        print(f">>> 工具返回：{tool_result}")

        messages.append({"role": "assistant", "content": output})
        messages.append({"role": "user", "content": f"工具返回：{tool_result}，请继续回答。"})

    print("\n" + "=" * 60)
    return output


if __name__ == "__main__":
    questions = [
        "特斯拉是哪一年成立的？",
        "2*3+5等于多少？"
    ]

    for q in questions:
        print("\n" + "=" * 60)
        toolformer_inference(q)
