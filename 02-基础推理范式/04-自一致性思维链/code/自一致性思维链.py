import sys
import time
from pathlib import Path
from collections import Counter
import re
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

system_prompt = """你是智能座舱的数学推理助手。
请先写出推理过程，然后在最后用以下格式给出最终答案：
最终答案：XXX"""


def extract_final_answer(text: str) -> str:
    match = re.search(r"最终答案[：:]\s*(.+)", text)
    if match:
        return match.group(1).strip()
    return text.strip()


def call_llm_once(question: str, chain_idx: int) -> Tuple[str, str]:
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{question}\n\n让我们一步步思考。"}
        ]
        
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2",
            messages=messages,
            stream=False,
            temperature=0.7
        )
        
        reasoning = response.choices[0].message.content
        answer = extract_final_answer(reasoning)
        return reasoning, answer
    except Exception as e:
        print(f"【推理链 {chain_idx} 异常】{str(e)}")
        return "", ""


def self_consistency_serial(question: str, num_chains: int = 3) -> Tuple[str, float]:
    start_time = time.time()
    all_answers = []
    all_reasonings = []
    
    print(f"\n{'='*60}")
    print(f"【串行模式】生成 {num_chains} 条推理链")
    
    for i in range(num_chains):
        reasoning, answer = call_llm_once(question, i + 1)
        if reasoning:
            all_reasonings.append(reasoning)
            all_answers.append(answer)
            print(f"\n【推理链 {i+1}】")
            print(reasoning)
            print(f"【提取答案】{answer}")
    
    final_answer = ""
    if all_answers:
        print(f"\n{'='*60}")
        print(f"【投票统计】")
        counter = Counter(all_answers)
        for ans, cnt in counter.most_common():
            print(f"  {ans}: {cnt} 票")
        final_answer = counter.most_common(1)[0][0]
    
    elapsed_time = time.time() - start_time
    return final_answer, elapsed_time


def self_consistency_parallel(question: str, num_chains: int = 3) -> Tuple[str, float]:
    start_time = time.time()
    all_answers = []
    all_reasonings = []
    
    print(f"\n{'='*60}")
    print(f"【并行模式】生成 {num_chains} 条推理链")
    
    with ThreadPoolExecutor(max_workers=num_chains) as executor:
        futures = {executor.submit(call_llm_once, question, i + 1): i + 1 for i in range(num_chains)}
        
        for future in as_completed(futures):
            chain_idx = futures[future]
            try:
                reasoning, answer = future.result()
                if reasoning:
                    all_reasonings.append((chain_idx, reasoning))
                    all_answers.append(answer)
            except Exception as e:
                print(f"【推理链 {chain_idx} 执行异常】{str(e)}")
    
    all_reasonings.sort(key=lambda x: x[0])
    for chain_idx, reasoning in all_reasonings:
        print(f"\n【推理链 {chain_idx}】")
        print(reasoning)
        print(f"【提取答案】{extract_final_answer(reasoning)}")
    
    final_answer = ""
    if all_answers:
        print(f"\n{'='*60}")
        print(f"【投票统计】")
        counter = Counter(all_answers)
        for ans, cnt in counter.most_common():
            print(f"  {ans}: {cnt} 票")
        final_answer = counter.most_common(1)[0][0]
    
    elapsed_time = time.time() - start_time
    return final_answer, elapsed_time


if __name__ == "__main__":
    question = "一个笼子里有鸡和兔子，共25个头，70只脚，鸡和兔子各几只？"
    num_chains = 3
    
    print(f"\n【问题】{question}")
    print(f"【推理链数量】{num_chains}")
    
    answer_serial, time_serial = self_consistency_serial(question, num_chains)
    answer_parallel, time_parallel = self_consistency_parallel(question, num_chains)
    
    print(f"\n{'='*60}")
    print(f"【耗时对比】")
    print(f"  串行模式: {time_serial:.2f} 秒")
    print(f"  并行模式: {time_parallel:.2f} 秒")
    if time_parallel > 0:
        speedup = time_serial / time_parallel
        print(f"  加速比: {speedup:.2f}x")
    print(f"\n【最终答案】串行={answer_serial} | 并行={answer_parallel}")
