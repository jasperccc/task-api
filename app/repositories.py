from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task


class TaskRepository:
    """负责访问任务数据。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, task: Task) -> Task:
        """将任务加入当前事务并执行 INSERT。"""

        self.session.add(task)
        await self.session.flush()
        return task

    async def commit(self) -> None:
        """提交当前事务。"""

        await self.session.commit()

    async def rollback(self) -> None:
        """回滚当前事务。"""

        await self.session.rollback()

    async def list_all(
        self, status: str | None = None, min_priority: int | None = None
    ) -> list[Task]:
        """按可选条件筛选任务，并按照 id 升序返回。"""
        statement = select(Task)

        if status is not None:
            statement = statement.where(Task.status == status)

        if min_priority is not None:
            statement = statement.where(Task.priority >= min_priority)

        statement = statement.order_by(Task.id)
        result = await self.session.scalars(statement)

        return list(result.all())

    async def get_by_id(self, task_id: int) -> Task | None:
        """根据主键查询任务。"""

        return await self.session.get(Task, task_id)

    async def delete(self, task: Task) -> None:
        """删除任务。"""

        await self.session.delete(task)
        await self.session.flush()
