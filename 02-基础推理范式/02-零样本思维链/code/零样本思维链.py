import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

system_prompt = """你是智能座舱的数学推理助手。"""


def zero_shot_cot_reasoning(question: str):
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
        "一个笼子里有鸡和兔子，共20个头，56只脚，鸡和兔子各几只？",
        "汽车以60km/h的速度行驶，3小时后行驶了多少公里？"
    ]
    
    for i, q in enumerate(questions, 1):
        print(f"\n\n【问题 {i}】{q}")
        print("【推理】", end="")
        zero_shot_cot_reasoning(q)