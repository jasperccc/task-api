import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_missing_task_returns_404(client: AsyncClient) -> None:
    """查询不存在的任务时应该返回 404。"""

    response = await client.get("/api/tasks/0")

    assert response.status_code == 404
    assert response.json() == {"detail": "任务不存在"}


@pytest.mark.asyncio
async def test_update_task_rejects_invalid_status(client: AsyncClient) -> None:
    """更新任务时应该拒绝非法状态。"""
    response = await client.patch(
        "/api/tasks/2",
        json={"status": "INVALID"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_returns_created_task(client: AsyncClient) -> None:
    """创建任务应该返回 201 和已创建的数据。"""
    response = await client.post(
        "/api/tasks",
        json={"title": "测试创建任务"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "测试创建任务",
        "status": "PENDING",
        "priority": 1,
    }


@pytest.mark.asyncio
async def test_update_task_persists_changes(client: AsyncClient) -> None:
    """更新任务后，新请求应该查询到更新结果。"""
    create_response = await client.post(
        "/api/tasks",
        json={"title": "更新前标题"},
    )
    task_id = create_response.json()["id"]

    update_response = await client.patch(
        f"/api/tasks/{task_id}",
        json={
            "title": "更新后标题",
            "status": "DONE",
            "priority": 1,
        },
    )

    get_response = await client.get(f"/api/tasks/{task_id}")

    assert update_response.status_code == 200
    assert update_response.json() == {
        "id": task_id,
        "title": "更新后标题",
        "status": "DONE",
        "priority": 1,
    }

    assert get_response.status_code == 200
    assert get_response.json() == update_response.json()


@pytest.mark.asyncio
async def test_delete_task_removes_task(client: AsyncClient) -> None:
    """删除任务后应该无法再次查询。"""
    create_response = await client.post(
        "/api/tasks",
        json={"title": "等待删除的任务"},
    )
    task_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/tasks/{task_id}")
    get_response = await client.get(f"/api/tasks/{task_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "任务不存在"}


@pytest.mark.asyncio
async def test_list_tasks_returns_tasks_in_id_order(client: AsyncClient) -> None:
    """任务列表应该按照 id 升序返回。"""
    await client.post(
        "/api/tasks",
        json={"title": "第一个任务"},
    )
    await client.post(
        "/api/tasks",
        json={"title": "第二个任务"},
    )

    response = await client.get("/api/tasks")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "第一个任务",
            "status": "PENDING",
            "priority": 1,
        },
        {
            "id": 2,
            "title": "第二个任务",
            "status": "PENDING",
            "priority": 1,
        },
    ]


@pytest.mark.asyncio
async def test_create_task_persists_priority(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/tasks",
        json={"title": "高优先级任务", "priority": 4},
    )
    task_id = create_response.json()["id"]

    get_response = await client.get(f"/api/tasks/{task_id}")

    assert create_response.status_code == 201
    assert get_response.status_code == 200
    assert get_response.json()["priority"] == 4


@pytest.mark.asyncio
async def test_create_task_rejects_invalid_priority(client: AsyncClient) -> None:
    """创建任务时应该拒绝非法优先级。"""
    response = await client.post(
        "/api/tasks",
        json={
            "title": "非法优先级任务",
            "priority": 6,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_tasks_filters_by_status_and_min_priority(
    client: AsyncClient,
) -> None:
    """任务列表应该同时按照状态和最低优先级筛选。"""
    await client.post(
        "/api/tasks",
        json={"title": "任务 A", "priority": 1},
    )
    await client.post(
        "/api/tasks",
        json={"title": "任务 B", "priority": 4},
    )
    task_c_response = await client.post(
        "/api/tasks",
        json={"title": "任务 C", "priority": 5},
    )
    task_c_id = task_c_response.json()["id"]
    await client.patch(
        f"/api/tasks/{task_c_id}",
        json={"status": "DONE"},
    )

    response = await client.get(
        "/api/tasks",
        params={
            "status": "PENDING",
            "min_priority": 3,
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 2,
            "title": "任务 B",
            "status": "PENDING",
            "priority": 4,
        },
    ]


@pytest.mark.asyncio
async def test_list_tasks_returns_empty_list_when_no_matches(
    client: AsyncClient,
) -> None:
    """没有符合条件的任务时应该返回空列表。"""
    await client.post(
        "/api/tasks",
        json={"title": "低优先级任务", "priority": 1},
    )

    response = await client.get(
        "/api/tasks",
        params={
            "status": "PENDING",
            "min_priority": 5,
        },
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("min_priority", [0, 6])
@pytest.mark.asyncio
async def test_list_tasks_rejects_invalid_min_priority(
    client: AsyncClient, min_priority: int
) -> None:
    """最低优先级超出范围时应该返回 422。"""
    response = await client.get(
        "/api/tasks",
        params={"min_priority": min_priority},
    )

    assert response.status_code == 422
