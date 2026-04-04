import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

system_prompt = """你是智能座舱的数学推理助手。
请用清晰的步骤解答问题，先写出推理过程，再给出最终答案。"""


def cot_math_reasoning(question: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{question}\n\n让我们一步步思考。"}
    ]
    
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2",
        messages=messages,
        stream=True
    )
    
    for chunk in response:
        if not chunk.choices:
            continue
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
        if chunk.choices[0].delta.reasoning_content:
            print(chunk.choices[0].delta.reasoning_content, end="", flush=True)


if __name__ == "__main__":
    questions = [
        "小明有15颗糖，给了小红4颗，又买了8颗，现在有多少颗？",
        "停车场有3排车，每排6辆，又开来了12辆，现在一共有多少辆？"
    ]
    
    for i, q in enumerate(questions, 1):
        print(f"\n\n【问题 {i}】{q}")
        print("【推理】", end="")
        cot_math_reasoning(q)
