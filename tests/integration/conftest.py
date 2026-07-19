"""
集成测试共享 fixtures（需要真实 Redmine）
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """TestClient"""
    from main import app
    return TestClient(app)


@pytest.fixture(scope="module")
def admin_headers(client):
    """管理员登录 Token"""
    resp = client.post("/api/v1/login", data={
        "username": "admin", "password": "admin123",
    })
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def cleanup_ids(client, admin_headers):
    """测试结束后批量清理测试数据"""
    ids = []

    yield ids

    if ids:
        client.post("/api/v1/employees/batch-delete", json=ids, headers=admin_headers)
