# Task API

使用 FastAPI、SQLAlchemy 和 PostgreSQL 实现的异步任务管理 API。

## 功能

- 创建、查询、更新和删除任务
- 按状态筛选任务
- 按最低优先级筛选任务
- Pydantic 请求参数校验
- 统一业务异常处理
- Alembic 数据库迁移
- Pytest 接口集成测试
- Docker Compose 部署

## 技术栈

- Python 3.12
- FastAPI
- SQLAlchemy 2
- asyncpg
- PostgreSQL 17
- Alembic
- Pydantic 2
- Pytest
- Docker Compose
- uv

## 项目结构

```text
app/
├── config.py
├── database.py
├── dependencies.py
├── exceptions.py
├── main.py
├── models.py
├── repositories.py
├── routers.py
├── schemas.py
└── services.py

migrations/     Alembic 数据库迁移
tests/          自动化测试
Dockerfile      API 镜像构建文件
compose.yaml    服务器部署配置
compose.dev.yaml 本地开发补充配置
```

## 环境变量

复制示例文件：

```bash
cp .env.example .env
```

修改 `.env` 中的数据库密码。真实 `.env` 不应提交到 Git。

## 本地启动

启动 API 和 PostgreSQL：

```bash
docker compose \
  -f compose.yaml \
  -f compose.dev.yaml \
  up -d --build
```

查看容器状态：

```bash
docker compose \
  -f compose.yaml \
  -f compose.dev.yaml \
  ps
```

Compose 会在 API 启动前自动执行：

```bash
alembic upgrade head
```

## 接口

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| GET | `/health` | API 健康检查 |
| GET | `/health/database` | 数据库健康检查 |
| POST | `/api/tasks` | 创建任务 |
| GET | `/api/tasks` | 查询任务列表 |
| GET | `/api/tasks/{task_id}` | 查询单个任务 |
| PATCH | `/api/tasks/{task_id}` | 更新任务 |
| DELETE | `/api/tasks/{task_id}` | 删除任务 |

任务列表支持可选查询参数：

```text
status=PENDING
status=DONE
min_priority=1～5
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

## 测试

测试使用独立数据库 `task_api_test`。

首次运行测试前创建测试数据库：

```bash
docker compose exec postgres \
  createdb -U task_api -O task_api task_api_test
```

将迁移应用到测试数据库：

```bash
DATABASE_URL="postgresql+asyncpg://task_api:task_api_password@127.0.0.1:5433/task_api_test" \
uv run alembic upgrade head
```

运行测试：

```bash
uv run pytest -v
```

运行代码检查和格式检查：

```bash
uv run ruff check app tests
uv run ruff format --check app tests
```

## 服务器部署

服务器只使用基础配置：

```bash
docker compose up -d --build
```

生产配置具有以下限制：

- PostgreSQL 不向宿主机发布端口
- API 仅监听宿主机的 `127.0.0.1:8000`
- 公网请求需要通过 Nginx 转发
- 服务器使用独立 `.env` 保存真实数据库密码
- `.env` 不得提交到 Git