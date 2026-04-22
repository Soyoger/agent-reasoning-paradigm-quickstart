import sys
from pathlib import Path
from openai import OpenAI
sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from config import base_url, api_key

from Planner import Planner
from Executor import Executor, get_mock_tools



if __name__ == "__main__":
    client = OpenAI(base_url=base_url,api_key=api_key)
    planner = Planner(client)
    while True:
        question = input("请输入用户的问题：")
        if question == "exit":
            break
        plan = planner.plan(question)   
        print("--- 计划生成完成 ---")
        tools = get_mock_tools()
        executor = Executor(client, tools=tools)
        result = executor.execute(question, plan)
        print("--- 计划执行完成 ---")
        print("\n执行结果如下：", "".join(result))