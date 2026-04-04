import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

few_shot_examples = [
    {
        "question": "小明有10颗糖，给了小红3颗，又买了5颗，现在有多少颗？",
        "reasoning": "小明一开始有10颗，给了小红3颗后剩7颗，又买了5颗，7+5=12。",
        "answer": "12"
    },
    {
        "question": "超市苹果5元一斤，买3斤需要多少钱？",
        "reasoning": "苹果5元一斤，买3斤就是5×3=15元。",
        "answer": "15元"
    }
]

examples_text = "\n\n"
for i, ex in enumerate(few_shot_examples, 1):
    examples_text += f"示例{i}：\n"
    examples_text += f"问：{ex['question']}\n"
    examples_text += f"推理：{ex['reasoning']}\n"
    examples_text += f"答案：{ex['answer']}\n\n"

system_prompt = f"""你是智能座舱的数学推理助手。
请先写出推理过程，再给出最终答案。
{examples_text}"""

print(f"系统提示：{system_prompt}\n\n")

def few_shot_cot_reasoning(question: str):
    prompt = f"{system_prompt}\n新问题：\n问：{question}\n推理："
    messages = [{"role": "user", "content": prompt}]
    
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
        "一个停车场有5排车位，每排8个，已经停了32辆，还剩多少个车位？",
        "汽车以80km/h的速度行驶，行驶240km需要几小时？"
    ]
    
    for i, q in enumerate(questions, 1):
        print(f"\n\n【问题 {i}】{q}")
        print("【推理+答案】", end="")
        few_shot_cot_reasoning(q)
