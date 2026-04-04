import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

system_prompt = """你是智能座舱的百科问答助手。用简洁、友好的语气回答用户问题。控制在100字以内。"""

def cockpit_encyclopedia_zero_shot(user_question: str):
    # 发送带有流式输出的请求
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        stream=True  # 启用流式输出
    )

    # 逐步接收并处理响应
    for chunk in response:
        if not chunk.choices:
            continue
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
        if chunk.choices[0].delta.reasoning_content:
            print(chunk.choices[0].delta.reasoning_content, end="", flush=True)


if __name__ == "__main__":
    questions = [
        "什么是自动驾驶？",
        "新能源汽车和燃油车有什么区别？",
        "如何正确使用安全气囊？"
    ]
    
    for i, q in enumerate(questions, 1):
        print(f"\n\n【问题 {i}】{q}")
        print("【回答】", end="")
        cockpit_encyclopedia_zero_shot(q)
