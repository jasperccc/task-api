"""FastAPI 应用入口。"""

from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.exceptions import AppError
from app.routers import router as task_router

app = FastAPI(title="Task API")

app.include_router(task_router, prefix="/api")


@app.exception_handler(AppError)
async def handle_app_error(
    _request: Request,
    exc: AppError,
) -> JSONResponse:
    """将业务异常转换为 HTTP 响应。"""

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


SessionDependency = Annotated[
    AsyncSession,
    Depends(get_session),
]


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/database")
async def database_health(
    session: SessionDependency,
) -> dict[str, str]:
    await session.execute(text("SELECT 1"))
    return {"database": "ok"}
