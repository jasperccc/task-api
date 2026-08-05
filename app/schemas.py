from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """创建任务时，前端需要提交的数据。"""

    title: str = Field(min_length=1, max_length=200)
    priority: int = Field(default=1, ge=1, le=5)


class TaskResponse(BaseModel):
    """任务接口返回给前端的数据。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: str
    priority: int


class TaskUpdate(BaseModel):
    """更新任务时允许提交的数据。"""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    status: Literal["PENDING", "DONE"] | None = None
