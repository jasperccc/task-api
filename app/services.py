from app.exceptions import NotFoundError
from app.models import Task
from app.repositories import TaskRepository
from app.schemas import TaskCreate, TaskUpdate


class TaskService:
    """负责任务业务逻辑。"""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def create_task(self, data: TaskCreate) -> Task:
        """创建并保存任务。"""

        task = Task(title=data.title, priority=data.priority)

        try:
            created_task = await self.repository.add(task)
            await self.repository.commit()
        except Exception:
            await self.repository.rollback()
            raise

        return created_task

    async def list_tasks(
        self,
        status: str | None = None,
        min_priority: int | None = None,
    ) -> list[Task]:
        """查询全部任务。"""

        return await self.repository.list_all(status, min_priority)

    async def get_task(self, task_id: int) -> Task:
        """根据 id 获取任务。"""

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise NotFoundError("任务不存在")

        return task

    async def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        """更新任务。"""

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise NotFoundError("任务不存在")

        if data.title is not None:
            task.title = data.title

        if data.status is not None:
            task.status = data.status

        try:
            await self.repository.commit()
        except Exception:
            await self.repository.rollback()
            raise

        return task

    async def delete_task(self, task_id: int) -> None:
        """删除任务。"""

        task = await self.repository.get_by_id(task_id)

        if task is None:
            raise NotFoundError("任务不存在")

        try:
            await self.repository.delete(task)
            await self.repository.commit()
        except Exception:
            await self.repository.rollback()
            raise
