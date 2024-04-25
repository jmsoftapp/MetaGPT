import asyncio
from metagpt.roles import (
    Architect,
    Engineer,
    ProductManager,
    ProjectManager,
)
from metagpt.team import Team

async def startup(idea: str):
    company = Team()
    company.hire(
        [
            ProductManager(),
            Architect(),
            ProjectManager(),
            Engineer(),
        ]
    )
    company.invest(investment=3.0)  # 提供3美元的资金，如果超出就停止
    company.run_project(idea=idea)

    await company.run(n_round=5)  # 这个项目跑5轮

if __name__ == "__main__":
    asyncio.run(startup(idea="Write a user management API using FastAPI"))  

