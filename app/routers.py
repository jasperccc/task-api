from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from app.dependencies import TaskServiceDependency
from app.models import Task
from app.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    data: TaskCreate,
    service: TaskServiceDependency,
) -> Task:

    return await service.create_task(data)


@router.get(
    "",
    response_model=list[TaskResponse],
)
async def list_tasks(
    service: TaskServiceDependency,
    status: Literal["PENDING", "DONE"] | None = None,
    min_priority: Annotated[
        int | None,
        Query(ge=1, le=5),
    ] = None,
) -> list[Task]:

    return await service.list_tasks(status, min_priority)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    task_id: int,
    service: TaskServiceDependency,
) -> Task:

    return await service.get_task(task_id)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    service: TaskServiceDependency,
) -> Task:

    return await service.update_task(task_id, data)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_id: int,
    service: TaskServiceDependency,
) -> None:

    await service.delete_task(task_id)
