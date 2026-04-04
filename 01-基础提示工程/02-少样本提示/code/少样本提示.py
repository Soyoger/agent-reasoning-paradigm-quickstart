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
        "user": "什么是自动驾驶？",
        "assistant": "自动驾驶是汽车通过传感器、AI等技术，无需人工操作就能自动行驶的系统。"
    },
    {
        "user": "新能源汽车和燃油车有什么区别？",
        "assistant": "新能源汽车用电驱动，环保节能；燃油车靠汽油，有尾气排放。"
    }
]

examples_text = "\n\n示例：\n"
for example in few_shot_examples:
    examples_text += f"\n用户：{example['user']}\n"
    examples_text += f"输出：{example['assistant']}\n"

system_prompt = f"""你是智能座舱的百科问答助手。
用简洁、友好的语气回答用户问题。
控制在100字以内。
{examples_text}"""


def cockpit_encyclopedia_few_shot(user_question: str):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
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
        "如何正确使用安全气囊？",
        "什么是ABS防抱死系统？"
    ]
    
    for i, q in enumerate(questions):
        print(f"\n\n【问题 {i+1}】{q}")
        print(f"【回答 {i+1}】", end="")
        cockpit_encyclopedia_few_shot(q)
