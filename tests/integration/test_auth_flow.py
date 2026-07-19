"""
集成测试：登录认证完整流程
"""
import pytest


@pytest.mark.integration
class TestAuthFlow:
    """认证完整链路"""

    def test_full_login_logout_relogin(self, client):
        """登录 → 退出 → 重新登录 → Token 失效"""
        # 1. 登录
        resp = client.post("/api/v1/login", data={
            "username": "admin", "password": "admin123",
        })
        assert resp.status_code == 200
        token1 = resp.json()["data"]["access_token"]

        # 2. 访问受保护接口
        headers1 = {"Authorization": f"Bearer {token1}"}
        resp = client.get("/api/v1/me", headers=headers1)
        assert resp.status_code == 200
        assert resp.json()["data"]["username"] == "admin"

        # 3. 退出
        resp = client.post("/api/v1/logout", headers=headers1)
        assert resp.status_code == 200

        # 4. 退出后 Token 失效
        resp = client.get("/api/v1/me", headers=headers1)
        assert resp.status_code == 401

        # 5. 重新登录获取新 Token
        resp = client.post("/api/v1/login", data={
            "username": "admin", "password": "admin123",
        })
        assert resp.status_code == 200
        token2 = resp.json()["data"]["access_token"]
        assert token2 != token1  # 不同 Token

        # 6. 新 Token 可用
        headers2 = {"Authorization": f"Bearer {token2}"}
        resp = client.get("/api/v1/me", headers=headers2)
        assert resp.status_code == 200

    def test_permission_chain(self, client):
        """权限链路：无 Token → 登录 → 访问 → 退出 → 拦截"""
        # 无 Token
        resp = client.get("/api/v1/employees")
        assert resp.status_code == 401

        # 错误 Token
        headers = {"Authorization": "Bearer invalid.token.here"}
        resp = client.get("/api/v1/employees", headers=headers)
        assert resp.status_code == 401

        # 登录
        resp = client.post("/api/v1/login", data={
            "username": "admin", "password": "admin123",
        })
        token = resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 正常访问
        resp = client.get("/api/v1/me", headers=headers)
        assert resp.status_code == 200

        # 退出
        resp = client.post("/api/v1/logout", headers=headers)
        assert resp.status_code == 200

        # 退出后无法访问
        resp = client.get("/api/v1/me", headers=headers)
        assert resp.status_code == 401
