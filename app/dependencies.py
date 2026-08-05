from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories import TaskRepository
from app.services import TaskService

SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


async def get_task_service(
    session: SessionDependency,
) -> TaskService:
    """组装任务 Service 及其依赖。"""

    repository = TaskRepository(session)
    return TaskService(repository)


TaskServiceDependency = Annotated[
    TaskService,
    Depends(get_task_service),
]
