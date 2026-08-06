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
| GET | `/` | 返回服务基本信息 |
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

### 生产环境验证

```bash
docker compose ps
curl -i https://api.example.com/health
curl -i https://api.example.com/health/database
```

### 发布新版本

本项目使用 Git tag 和镜像 tag 对应版本。发布前先在本地完成测试和代码检查：

```bash
uv run ruff check app tests
uv run ruff format --check app tests
uv run pytest -v
```

服务器更新代码并重建 API 镜像：

```bash
git fetch origin --tags
git switch main
git pull --ff-only origin main

docker compose up -d --build api
docker compose ps
```

### 回退应用版本

应用代码可以回退，但不能把数据库迁移盲目回退。回退到已有版本的 Git tag，并使用对应的旧镜像：

```bash
git fetch origin --tags
git switch --detach v0.1.0
docker compose up -d --no-build api
```

回退后验证接口和已有数据：

```bash
curl -i https://api.example.com/
curl -s https://api.example.com/api/tasks/2
```

恢复最新版本：

```bash
git switch main
git pull --ff-only origin main
docker compose up -d --no-build api
```

### PostgreSQL 备份

备份文件保存在服务器主机目录，不依赖容器生命周期：

```bash
install -d -m 700 ~/backups/task-api

BACKUP_FILE="$HOME/backups/task-api/task_api_$(date +%Y%m%d_%H%M%S).dump"

docker compose exec -T postgres \
  pg_dump -U task_api -d task_api -Fc \
  > "$BACKUP_FILE"

chmod 600 "$BACKUP_FILE"
ls -lh "$BACKUP_FILE"
```

### 恢复验证

不要直接恢复到正式数据库，先恢复到临时数据库：

```bash
BACKUP_FILE="$(ls -t "$HOME"/backups/task-api/*.dump | head -n 1)"

docker compose exec -T postgres \
  createdb -U task_api task_api_restore_test

docker compose exec -T postgres \
  pg_restore -U task_api \
  -d task_api_restore_test \
  --no-owner \
  --no-privileges \
  < "$BACKUP_FILE"

docker compose exec -T postgres \
  psql -U task_api -d task_api_restore_test \
  -c "\dt" \
  -c "SELECT version_num FROM alembic_version;" \
  -c "SELECT COUNT(*) AS task_count FROM tasks;"

docker compose exec -T postgres \
  dropdb -U task_api task_api_restore_test
```

### 常用排障命令

```bash
docker compose ps
docker compose logs api --tail=50
docker compose logs postgres --tail=50
docker compose exec api printenv DATABASE_URL
sudo nginx -t
sudo tail -n 50 /var/log/nginx/access.log
sudo tail -n 50 /var/log/nginx/error.log
```
