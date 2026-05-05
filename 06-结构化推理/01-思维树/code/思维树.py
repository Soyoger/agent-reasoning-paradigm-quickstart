import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

# 将项目根目录添加到路径以便导入 config
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

class ToTPlanner:
    """
    思维树 (ToT) 规划器
    架构本质：将 LLM 作为状态机生成器，结合搜索算法进行多路径探索。
    """
    
    def __init__(self, model: str = "deepseek-ai/DeepSeek-V3.2"):
        self.model = model

    def generate_thoughts(self, problem: str, current_state: str, k: int = 3) -> List[str]:
        """
        思维生成 (Thought Generator)
        根据当前状态，生成 k 个可能的下一步动作或思路。
        """
        prompt = f"""问题: {problem}
                    当前进度: {current_state}
                    请为下一步生成 {k} 个不同的合理方案。
                    每个方案一行，不要包含多余的文字。
                """
        print(f"生成的思维提示词: {prompt}")
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        thoughts = response.choices[0].message.content.strip().split('\n')
        return [t.strip("- ") for t in thoughts][:k]

    def evaluate_state(self, problem: str, current_state: str) -> str:
        """
        状态评估器 (State Evaluator)
        评估当前路径的前景：Sure (确定可行), Maybe (可能可行), Impossible (不可行)。
        """
        prompt = f"""问题: {problem}
                    当前路径: {current_state}
                    评估此路径解决问题的可能性。仅从以下三个词中选择一个输出：
                    - Sure: 方案非常合理，且接近目标
                    - Maybe: 方案有一定道理，需要进一步展开
                    - Impossible: 方案存在逻辑漏洞或无法满足约束

                    评估结果:"""
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def solve(self, problem: str, max_steps: int = 3, beam_width: int = 2):
        """
        搜索算法 (使用简化版的束搜索 Beam Search)
        """
        print(f"🚀 开始解决问题: {problem}\n")
        
        # 初始状态
        # 每个状态包含：当前的推理路径文本
        states = [""]
        
        for step in range(max_steps):
            print(f"--- 步骤 {step + 1} ---")
            new_candidates = []
            
            for state in states:
                # 1. 生成新思维
                thoughts = self.generate_thoughts(problem, state, k=3)
                print(f"生成的思维: {thoughts}")
                
                for t in thoughts:
                    new_state = f"{state} -> {t}" if state else t
                    
                    # 2. 评估新状态
                    evaluation = self.evaluate_state(problem, new_state)
                    print(f"检测路径: {new_state[:60]}... | 评估: {evaluation}")
                    
                    if "Impossible" not in evaluation:
                        # 记录得分，用于束搜索排序 (这里简化为 Sure 优先)
                        score = 2 if "Sure" in evaluation else 1
                        new_candidates.append((new_state, score))
            
            # 3. 束搜索：根据评分保留前 beam_width 个状态
            new_candidates.sort(key=lambda x: x[1], reverse=True)
            states = [x[0] for x in new_candidates[:beam_width]]
            
            if not states:
                print("❌ 搜索失败：所有路径均不可行。")
                return None
            
            print(f"保留状态数: {len(states)}\n")

        print("✅ 找到最优解路径:")
        for i, final_path in enumerate(states):
            print(f"路径 {i+1}: {final_path}")
        return states

if __name__ == "__main__":
    planner = ToTPlanner()
    
    # 案例：智能座舱多任务规划
    cockpit_problem = "今天下午3点前要去接孩子，路上要买束花，还要顺便给车充个电。现在1:30，请规划最省时路线。"
    
    planner.solve(cockpit_problem, max_steps=3, beam_width=2)
