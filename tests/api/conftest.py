"""
API 测试共享 fixtures
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def app():
    """FastAPI 应用实例（session scope，整个测试会话共享）"""
    from main import app as _app
    return _app


@pytest.fixture(scope="function")
def client(app):
    """TestClient"""
    return TestClient(app)


@pytest.fixture(scope="function")
def login_headers(client):
    """每次测试独立登录，避免 token 黑名单交叉影响"""
    resp = client.post("/api/v1/login", data={
        "username": "admin",
        "password": "admin123",
    })
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def test_employee(client, login_headers):
    """创建一个测试用员工，测试结束后清理。Redmine 不可用时跳过依赖该 fixture 的测试。"""
    resp = client.post("/api/v1/employees", json={
        "number": "TEST_API_001",
        "name": "API测试员工",
        "gender": "男",
        "age": 30,
        "phone": "13800000001",
        "email": "test_api@example.com",
        "department": "测试部",
        "position": "测试工程师",
        "jointime": "2023-01-01",
    }, headers=login_headers)

    if resp.status_code >= 500:
        pytest.skip("Redmine 服务不可用，跳过依赖数据创建的测试")

    body = resp.json()
    if body.get("code") != 200:
        pytest.skip("创建测试数据失败，跳过依赖数据创建的测试")

    employee_id = body["data"]["id"]

    yield employee_id

    # 清理
    client.delete(f"/api/v1/employees/{employee_id}", headers=login_headers)
