import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# 将项目根目录添加到路径以便导入 config
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from openai import OpenAI
from config import base_url, api_key

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

class GoTPlanner:
    """
    思维图 (GoT) 规划器
    架构本质：将推理建模为图，支持思维的并行生成、交叉验证与聚合。
    """
    
    def __init__(self, model: str = "deepseek-ai/DeepSeek-V3.2"):
        self.model = model

    def generate_sub_tasks(self, task: str) -> List[str]:
        """将主任务分解为可以并行处理的子任务 (思维节点生成)"""
        prompt = f"针对任务：'{task}'，请将其拆解为2-3个可以独立分析的子维度。每行一个维度，不要序号。"
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip().split('\n')

    def solve_sub_task(self, sub_task: str) -> str:
        """解决具体的子任务"""
        print(f"正在并行分析节点: {sub_task}...")
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": f"请简要分析并给出建议：{sub_task}"}]
        )
        return response.choices[0].message.content.strip()

    def aggregate_thoughts(self, task: str, thoughts: List[str]) -> str:
        """
        聚合 (Aggregation) 变换：将多个思维节点的信息合并
        这是 GoT 区别于 ToT 的关键操作
        """
        print("\n🚀 正在执行【聚合变换】，汇总各节点信息...")
        combined_context = "\n".join([f"维度{i+1}分析: {t}" for i, t in enumerate(thoughts)])
        prompt = f"""原始任务: {task}
各维度的独立分析结论如下:
{combined_context}

请综合上述所有信息，进行交叉验证，指出冲突点并给出最终的集成方案。"""
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def run_got_flow(self, main_task: str):
        print(f"🌟 开始执行思维图 (GoT) 流程\n主任务: {main_task}\n")
        
        # 1. 生成并行节点
        sub_tasks = self.generate_sub_tasks(main_task)
        
        # 2. 并行处理各节点 (模拟图的并行分支)
        node_results = []
        for st in sub_tasks:
            result = self.solve_sub_task(st)
            node_results.append(result)
        
        # 3. 聚合变换 (将图中的多条边汇聚到一个节点)
        final_answer = self.aggregate_thoughts(main_task, node_results)
        
        print("\n" + "="*50)
        print("✅ 思维图最终聚合方案:")
        print(final_answer)
        print("="*50)

if __name__ == "__main__":
    planner = GoTPlanner()
    
    # 案例：智能座舱多维行程规划
    travel_task = "策划一个上海3天行程：包含浦东商务会议、外滩旅游、且必须包含一家地道的本帮菜和一家川菜，需考虑通勤效率。"
    
    planner.run_got_flow(travel_task)
