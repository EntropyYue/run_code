import os
import typing
import requests
import json
from pydantic import BaseModel, Field


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


def get_end_output(response: requests.Response):

    output = response.json()["result"][0]["cells"][-1]["outputs"]

    if output == []:
        return "not output."

    if response.status_code == 200:
        return output[0]["text"]


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
        在Jupyter Notebook中运行Python代码

        :param code: 要运行的Python代码，代码将在一个有状态的ipython环境中运行

        :return: 一个包含以下字段的json对象：`input`, `output`
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

            await emitter.message(
                f"在Jupyter Notebook中执行了\n```python\n{code}\n```\n返回的结果是\n```返回\n{get_end_output(self.response)}\n```\n"
            )

            return json.dumps(
                {
                    "代码输入": code,
                    "在Jupyter Notebook中执行的返回": get_end_output(self.response),
                },
                ensure_ascii=False,
            )
        else:
            await emitter.emit(
                status="error",
                description="代码执行出现错误",
                done=True
            )

            return "代码执行出现错误"
