from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import settings
from app.database import get_session
from app.main import app

test_database_url = make_url(settings.database_url).set(
    database="task_api_test",
)

test_engine = create_async_engine(
    test_database_url,
    poolclass=NullPool,
)

test_session_factory = async_sessionmaker(
    bind=test_engine,
    expire_on_commit=False,
)


async def get_test_session() -> AsyncIterator[AsyncSession]:
    """为测试请求提供测试数据库 Session。"""

    async with test_session_factory() as session:
        yield session


app.dependency_overrides[get_session] = get_test_session


# autouse表示每条测试都会自动使用该fixture
@pytest_asyncio.fixture(autouse=True)
async def reset_test_database() -> AsyncIterator[None]:
    """每条测试前后清空测试任务数据。"""

    # 测试前清空数据库
    async with test_engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY"))

    yield
    # 测试后再次清空数据库
    async with test_engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY"))


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """为接口测试提供异步客户端。"""

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client
