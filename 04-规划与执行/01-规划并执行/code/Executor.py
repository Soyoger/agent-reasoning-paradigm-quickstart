

import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from openai import OpenAI
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from config import base_url, api_key
from MockTools import get_mock_tools, execute_mock_tool

default_system_prompt = """你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
请专注于解决当前步骤，并输出该步骤的最终答案。"""


def call_llm(
    client,
    messages: List[Dict],
    tools: Optional[List[Dict]] = None,
    model: str = "deepseek-ai/DeepSeek-V3.2",
    **kwargs
) -> Any:
    """
    公共方法：调用大模型（支持Function Calling）

    Args:
        client: LLM客户端实例
        messages: 消息历史
        tools: 工具定义列表（可选）
        model: 模型名称
        **kwargs: 其他参数

    Returns:
        LLM响应对象
    """
    params = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": 0.3
    }
    if tools:
        params["tools"] = tools
        params["tool_choice"] = "auto"
    params.update(kwargs)

    return client.chat.completions.create(**params)


class Executor:
    """执行器 - 负责按计划逐步执行（支持 Function Calling）"""

    def __init__(
        self,
        llm_client,
        system_prompt: Optional[str] = None,
        tools: Optional[List] = [],
        enable_tool_calling: bool = True,
        max_tool_iterations: int = 3
    ):
        self.llm_client = llm_client
        self.system_prompt = system_prompt or default_system_prompt
        self.tools = tools
        self.enable_tool_calling = enable_tool_calling and tools is not None
        self.max_tool_iterations = max_tool_iterations

    def execute(self, question: str, plan: List[str], **kwargs) -> str:
        """
        按计划执行任务（支持 Function Calling）

        Args:
            question: 原始问题
            plan: 执行计划
            **kwargs: LLM调用参数

        Returns:
            最终答案
        """
        history = []
        final_answer = ""

        print("\n--- 正在执行计划 ---")
        for i, step in enumerate(plan, 1):
            print(f"\n-> 正在执行步骤 {i}/{len(plan)}: {step}")

            # 构建上下文消息
            context = f"""# 原始问题:
                                {question}

                                # 完整计划:
                                {self._format_plan(plan)}

                                # 历史步骤与结果:
                                {self._format_history(history) if history else "无"}

                                # 当前步骤:
                                {step}

                                请执行当前步骤并给出结果，当前结果限制100字以内。"""

            # 执行单个步骤（支持工具调用）
            response_text = self._execute_step(context, **kwargs)

            history.append({"step": step, "result": response_text})
            final_answer = response_text
            print(f"✅ 步骤 {i} 已完成，结果: {final_answer}")

        return final_answer

    def _format_plan(self, plan: List[str]) -> str:
        """格式化计划列表"""
        return "\n".join([f"{i}. {step}" for i, step in enumerate(plan, 1)])

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """格式化历史记录"""
        return "\n\n".join([f"步骤 {i}: {h['step']}\n结果: {h['result']}"
                           for i, h in enumerate(history, 1)])

    def _execute_step(self, context: str, **kwargs) -> str:
        """
        执行单个步骤（支持 Function Calling）

        Args:
            context: 上下文信息
            **kwargs: 其他参数

        Returns:
            步骤执行结果
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context}
        ]

        # 如果没有启用工具调用，直接返回
        if not self.enable_tool_calling or not self.tools:
            response = call_llm(self.llm_client, messages, self.tools, **kwargs)
            message = response.choices[0].message
            return message.content if hasattr(message, 'content') else str(message)

        # 开始工具调用模式
        current_iteration = 0

        while current_iteration < self.max_tool_iterations:
            current_iteration += 1
             # 调用 LLM
            response = call_llm(self.llm_client, messages, self.tools, **kwargs)
            message = response.choices[0].message

            # 处理工具调用
            tool_calls = message.tool_calls
            if not tool_calls:
                # 没有工具调用，返回文本响应
                return message.content or ""

            # 将助手消息添加到历史
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })

            # 执行所有工具调用
            print(f"当前工具调用: {tool_calls}")
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_call_id = tool_call.id

                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    print(f"❌ 工具参数解析失败: {e}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": f"错误：参数格式不正确 - {str(e)}"
                    })
                    continue

                # 执行工具（复用基类方法）
                result = execute_mock_tool(tool_name, arguments)

                # 添加工具结果到消息
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": tool_name,
                    "content": result
                })

        # 如果超过最大迭代次数，获取最后一次回答
        if current_iteration >= self.max_tool_iterations:
            response = call_llm(self.llm_client, messages, self.tools, **kwargs)
            message = response.choices[0].message
            return message.content if hasattr(message, 'content') else str(message) 
        return ""

if __name__ == "__main__":
    client = OpenAI(base_url=base_url,api_key=api_key)
    tools = get_mock_tools()
    executor = Executor(client, tools=tools)
    plan = [
          "确定出发地点在上海市的具体位置或地标",
          "了解用户需要前往虹桥的具体地标（如虹桥机场、虹桥火车站或虹桥商务区）",
          "收集上海到虹桥的各种交通方式信息：地铁、公交、出租车、网约车等",
          "分析不同交通方式的费用成本、时间效率和便利性",
          "根据用户具体需求推荐最佳路线组合",
          "准备详细的路线引导说明，包括换乘点和注意事项"
    ]
    result = executor.execute("从陆家嘴触发上海到虹桥的交通路线",plan)
    print("\n 最终回复:", result)
