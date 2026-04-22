import sys
import json
from pathlib import Path
from typing import List, Optional
from openai import OpenAI
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from config import base_url, api_key
default_system_prompt = """你是资深 AI 任务拆解与流程规划专家。请根据用户复杂诉求，梳理逻辑链路，拆解为有序、独立、可落地执行的分步行动计划。要求单条步骤简洁明确、互不重叠，整体步骤总数不超过 6 个子任务；所有子任务执行完毕后，额外新增一步复盘总结整个流程，形成完整可执行方案。"""

class Planner:
    """规划器 - 负责将复杂问题分解为简单步骤（使用 Function Calling）"""

    def __init__(self, llm_client, system_prompt: Optional[str] = None):
        self.llm_client = llm_client
        self.system_prompt = system_prompt or default_system_prompt

    def plan(self, question: str, **kwargs) -> List[str]:
        """
        生成执行计划（使用 Function Calling）

        Args:
            question: 要解决的问题
            **kwargs: LLM调用参数

        Returns:
            步骤列表
        """
        print("--- 正在生成计划 ---")

        # 定义计划生成工具
        plan_tool = {
            "type": "function",
            "function": {
                "name": "generate_plan",
                "description": "生成解决问题的分步计划",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "steps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "按顺序排列的执行步骤列表"
                        }
                    },
                    "required": ["steps"]
                }
            }
        }

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"请为以下问题生成详细的执行计划：\n\n{question}"}
        ]

        try:
            response = self.llm_client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3.2",
                messages=messages,
                tools=[plan_tool],
                tool_choice={"type": "function", "function": {"name": "generate_plan"}},
                stream=False,
                **kwargs
            )
            # print(response)
            message = response.choices[0].message
            # 提取工具调用结果
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                arguments = json.loads(tool_call.function.arguments)
                plan = arguments.get("steps", [])

                print(f"✅ 计划已生成:")
                for i, step in enumerate(plan, 1):
                    idx = f"{i}."
                    if(step.strip().startswith(idx)):
                        print(f" {step}")
                    else:
                        print(f" {idx} {step}")

                return plan
            else:
                print("❌ 模型未返回计划工具调用")
                return []

        except Exception as e:
            print(f"❌ 生成计划时发生错误: {e}")
            return []

if __name__ == "__main__":
    client = OpenAI(base_url=base_url,api_key=api_key)
    planner = Planner(client)
    plan = planner.plan("上海到虹桥的交通路线")