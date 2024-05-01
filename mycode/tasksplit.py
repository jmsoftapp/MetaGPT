"""
Author: csw
"""
import re

from metagpt.actions import Action
from metagpt.config2 import config
from metagpt.const import METAGPT_ROOT
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message

#EXAMPLE_CODE_FILE = METAGPT_ROOT / "examples/build_customized_agent.py"
#MULTI_ACTION_AGENT_CODE_EXAMPLE = EXAMPLE_CODE_FILE.read_text()

#你是一个工作团队的负责人，你的工作是将一个任务分拆成多个可执行的子任务，你可参照下面示例中的格式来组织和输出子任务
#现在，您应该根据说明分拆任务，请仔细考虑，分拆后各子任应相互独立，且合理。
#{"后台管理":
    #[
    #{"用户管理"：“包括用户注册、登录、注销、用户资料编辑、权限管理等功能"},
    #{"内容管理":"文章、产品、页面等内容的增删改查（CRUD）操作、内容分类、标签管理"},
    #{"媒体管理":"图片、视频等媒体文件的上传、管理和删除"}
    #]
#}

MULTI_ACTION_AGENT_CODE_EXAMPLE = """
    {"Backend management":
        [
            {"User Management": "including functions such as user registration, login, logout, user profile editing, and permission management"},
            {"Content Management": "CRUD operations, content classification, and label management for articles, products, pages, and other content"},
            {"Media Management": "Uploading, managing, and deleting media files such as images and videos"}
        ]
    }
"""

class SplitTask(Action):
    PROMPT_TEMPLATE: str = """
    ### BACKGROUND
    You are the leader of a work team, and your job is to break down a task into multiple executable subtasks. You can refer to the format in the following example to organize and output subtasks:
    ### EXAMPLE STARTS AT THIS LINE
    {example}
    ### EXAMPLE ENDS AT THIS LINE
    ### TASK
    Now, you should split the tasks according to the instructions. Please carefully consider that after splitting, each sub task should be independent of each other and reasonable
    ### INSTRUCTION
    {instruction}
    ### Your answer:
    """

    async def run(self, example: str, instruction: str):
        prompt = self.PROMPT_TEMPLATE.format(example=example, instruction=instruction)
        # logger.info(prompt)

        rsp = await self._aask(prompt)

        #print(f"Answer:{rsp}")
        
        code_text = SplitTask.parse_code(rsp)

        return rsp

    @staticmethod
    def parse_code(rsp):
        """
        pattern = r"```python(.*)```"
        match = re.search(pattern, rsp, re.DOTALL)
        code_text = match.group(1) if match else ""
        config.workspace.path.mkdir(parents=True, exist_ok=True)
        new_file = config.workspace.path / "agent_created_agent.py"
        new_file.write_text(code_text)
        """

        code_text = rsp
        
        config.workspace.path.mkdir(parents=True, exist_ok=True)
        new_file = config.workspace.path / "tasksplit_output.txt"
        new_file.write_text(code_text)
        
        return code_text


class AgentCreator(Role):
    name: str = "Matrix"
    profile: str = "AgentCreator"
    agent_template: str = MULTI_ACTION_AGENT_CODE_EXAMPLE

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_actions([SplitTask])

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo
        msg = self.rc.memory.get()[-1]

        instruction = msg.content
        code_text = await SplitTask().run(example=self.agent_template, instruction=instruction)
        msg = Message(content=code_text, role=self.profile, cause_by=todo)

        return msg


if __name__ == "__main__":
    import asyncio

    async def main():
        agent_template = MULTI_ACTION_AGENT_CODE_EXAMPLE

        creator = AgentCreator(agent_template=agent_template)

        msg = "Backend management module implemented using FastAPI"
        await creator.run(msg)

    asyncio.run(main())
