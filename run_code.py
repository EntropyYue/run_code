import os
import typing
import requests
import json
import asyncio
from pydantic import BaseModel, Field


# 事件发射器处理
class EventEmitter:
    def __init__(self, event_emitter: typing.Callable[[dict], typing.Any] = None):
        self.event_emitter = event_emitter

    async def emit(self, description="未知状态", status="in_progress", done=False):
        if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )

    async def message(self, content):
        await self.event_emitter(
            {
                "type": "message",
                "data": {
                    "content": content,
                },
            }
        )

    async def citation(self, document, source = {"name": "run_code"}):
        await self.event_emitter(
            {
                "type": "citation",
                "data": {
                    "document": document,
                    "metadata": document,
                    "source": source,
                },
            }
        )

# <test>

# 事件发射器
async def __event_emitter__(__emitter__: dict):
    pass

# </test>

class Tools:
    class Valves(BaseModel):
        IPYTHON_API_BASE_URL: str = Field(
            default="http://127.0.0.1:8888",
            description="Jupyter Notebook API Base URL",
        )

    def __init__(
        self,
    ):
        self.valves = self.Valves()

    async def run_code(
        self,
        code: str,
        __event_emitter__: typing.Callable[[dict], typing.Any] = None
    ) -> str:
        """
        在Jupyter Notebook中运行iPython代码，使用"% "开头的代码来执行系统命令，例如：% ls

        :params code: 要运行的iPython代码，代码将在一个有状态的ipython环境中运行

        :return: 一个包含以下字段的json对象：`代码输入`, `在Jupyter Notebook中执行的返回`
        """
        emitter = EventEmitter(__event_emitter__)
        await emitter.emit("正在执行代码")

        self.data = {"code": code}
        
        # 发送请求
        self.response = requests.post(
            f"{self.valves.IPYTHON_API_BASE_URL}/api/v1/exec",
            data=json.dumps(self.data),
            headers={"Content-Type": "application/json"},
        )
        if self.response.status_code == 200:
            await emitter.emit(
                status="complete",
                description=f"代码执行成功",
                done=True,
            )

        else:
            await emitter.emit(
                status="error",
                description=f"代码执行失败",
                done=True,
            )

            await emitter.citation([code])

        return json.dumps(
            {
                "注释": "以下是你在Jupyter Notebook中执行的所有代码的输入和输出组成的json，最后一个字典是你执行的上一段代码",
                "exec": self.response.json(),
            },
                ensure_ascii=False,
            )


async def main():
    tools = Tools()
    print(
        await tools.run_code(
            """
            print("Hello, World!")
            """,
            __event_emitter__
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
