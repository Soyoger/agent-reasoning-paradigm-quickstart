import sys
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from openai import OpenAI
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from config import base_url, api_key
from Memory import Memory
from MockTools import get_mock_tools, execute_mock_tool


# 默认 system_prompt
default_system_prompt = """你是一个具有自我反思能力的AI助手。你的工作流程是：
                            1. 首先尝试完成用户的任务
                            2. 然后反思你的回答，找出可能的问题或改进空间
                            3. 根据反思结果优化你的回答
                            4. 如果回答已经很好，在反思时回复"无需改进"

                            请始终保持批判性思维，追求更高质量的输出。
                        """
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


class Reflection:
    """
    Reflection - 自我反思与迭代优化的智能体

    这个Agent能够：
    1. 执行初始任务
    2. 对结果进行自我反思
    3. 根据反思结果进行优化
    4. 迭代改进直到满意
    5. 支持工具调用（可选）

    特别适合代码生成、文档写作、分析报告等需要迭代优化的任务。

    使用标准 Function Calling 格式，通过 system_prompt 定义角色和行为。
    """

    def __init__(
        self,
        name: str,
        llm_client,
        system_prompt: Optional[str] = None,
        max_iterations: int = 3,
        tools: Optional[List] = [],
        enable_tool_calling: bool = True,
        max_tool_iterations: int = 3
    ):
        """
        初始化ReflectionAgent

        Args:
            name: Agent名称
            llm: LLM实例
            system_prompt: 系统提示词（定义角色和反思策略）
            config: 配置对象
            max_iterations: 最大迭代次数
            tool_registry: 工具注册表（可选）
            enable_tool_calling: 是否启用工具调用
            max_tool_iterations: 最大工具调用迭代次数
        """
        self.name = name
        self.llm_client = llm_client
        self.system_prompt = system_prompt or default_system_prompt
        self.max_iterations = max_iterations
        self.tools = tools
        self.memory = Memory()
        self.enable_tool_calling = enable_tool_calling and self.tools is not None
        self.max_tool_iterations = max_tool_iterations

    def run(self, input_text: str, **kwargs) -> str:
        """
        运行Reflection Agent

        Args:
            input_text: 任务描述
            **kwargs: 其他参数

        Returns:
            最终优化后的结果
        """
        print(f"\n🤖 {self.name} 开始处理任务: {input_text}")

        # 重置记忆
        self.memory = Memory()

        # 1. 初始执行
        print("\n--- 正在进行初始尝试 ---")
        initial_result = self._execute_task(input_text, **kwargs)
        print(f"\n--- 初始尝试结果 ---\n{initial_result}")
        self.memory.add_record("execution", initial_result)

        # 2. 迭代循环：反思与优化
        for i in range(self.max_iterations):
            print(f"\n--- 第 {i+1}/{self.max_iterations} 轮迭代 ---")

            # a. 反思
            print("\n-> 正在进行反思...")
            last_result = self.memory.get_last_execution()
            feedback = self._reflect_on_result(input_text, last_result, **kwargs)
            self.memory.add_record("reflection", feedback)

            # b. 检查是否需要停止
            if "无需改进" in feedback or "no need for improvement" in feedback.lower():
                print("\n✅ 反思认为结果已无需改进，任务完成。")
                break

            # c. 优化
            print("\n-> 正在进行优化...")
            refined_result = self._refine_result(input_text, last_result, feedback, **kwargs)
            self.memory.add_record("execution", refined_result)

        final_result = self.memory.get_last_execution()
        print(f"\n--- 任务完成 ---\n最终结果:\n{final_result}")

        # 保存到历史记录
        # self.add_message(Message(input_text, "user"))
        # self.add_message(Message(final_result, "assistant"))

        return final_result

    def _execute_task(self, task: str, **kwargs) -> str:
        """执行初始任务"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"请完成以下任务：\n\n{task}"}
        ]
        return self._get_llm_response(messages, **kwargs)

    def _reflect_on_result(self, task: str, result: str, **kwargs) -> str:
        """对结果进行反思"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""请仔细审查以下回答，并找出可能的问题或改进空间：
                    # 原始任务:
                    {task}

                    # 当前回答:
                    {result}

                    请分析这个回答的质量，指出不足之处，并提出具体的改进建议。
                    如果回答已经很好，请回答"无需改进"。"""}
        ]
        return self._get_llm_response(messages, **kwargs)

    def _refine_result(self, task: str, last_attempt: str, feedback: str, **kwargs) -> str:
        """根据反馈优化结果"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""请根据反馈意见改进你的回答：
                                            # 原始任务:
                                            {task}

                                            # 上一轮回答:
                                            {last_attempt}

                                            # 反馈意见:
                                            {feedback}

                                            请提供一个改进后的回答。"""}
        ]
        return self._get_llm_response(messages, **kwargs)

    def _get_llm_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        调用LLM并获取完整响应（支持 Function Calling）

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            LLM响应文本
        """
        # 如果没有启用工具调用，直接返回
        if not self.enable_tool_calling or not self.tools:
            response = call_llm(self.llm_client, messages, self.tools, **kwargs)
            message = response.choices[0].message
            return llm_response.content if hasattr(llm_response, 'content') else str(llm_response)

        # 启用工具调用模式
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
    reflection = Reflection(
        name="Reflection", 
        llm_client=client,
        system_prompt=default_system_prompt,
        max_iterations=3,
        tools=get_mock_tools(),
        enable_tool_calling=True,
        max_tool_iterations=3
        )
    while True:
        question = input("请输入用户的问题：")
        if question == "exit":
            break
        reflection.run(question)
