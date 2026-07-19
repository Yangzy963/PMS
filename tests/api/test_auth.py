"""
API 测试：认证模块
"""
import pytest


class TestLogin:
    """登录接口"""

    def test_login_success(self, client):
        """登录成功"""
        resp = client.post("/api/v1/login", data={
            "username": "admin",
            "password": "admin123",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert body["message"] == "登录成功"
        assert "access_token" in body["data"]
        assert body["data"]["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """登录失败：错误密码"""
        resp = client.post("/api/v1/login", data={
            "username": "admin",
            "password": "wrong",
        })
        assert resp.status_code == 401
        body = resp.json()
        assert body["code"] == 401

    def test_login_wrong_username(self, client):
        """登录失败：不存在用户"""
        resp = client.post("/api/v1/login", data={
            "username": "nobody",
            "password": "admin123",
        })
        assert resp.status_code == 401

    def test_login_empty_body(self, client):
        """登录失败：空参数"""
        resp = client.post("/api/v1/login", data={})
        assert resp.status_code == 422


class TestMe:
    """获取当前用户"""

    def test_get_me_with_token(self, client, login_headers):
        """有 Token 时获取用户信息"""
        resp = client.get("/api/v1/me", headers=login_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["username"] == "admin"

    def test_get_me_without_token(self, client):
        """无 Token 时拒绝访问"""
        resp = client.get("/api/v1/me")
        assert resp.status_code == 401


class TestLogout:
    """退出登录"""

    def test_logout_success(self, client):
        """退出登录成功（自建 token，不污染共享 fixture）"""
        resp = client.post("/api/v1/login", data={
            "username": "admin", "password": "admin123",
        })
        token = resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post("/api/v1/logout", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["message"] == "退出成功"

    def test_logout_without_token(self, client):
        """无 Token 退出"""
        resp = client.post("/api/v1/logout")
        assert resp.status_code == 401

    def test_token_invalid_after_logout(self, client):
        """退出后 Token 失效"""
        # 先登录获取 Token
        login_resp = client.post("/api/v1/login", data={
            "username": "admin", "password": "admin123",
        })
        token = login_resp.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 退出
        resp = client.post("/api/v1/logout", headers=headers)
        assert resp.status_code == 200

        # 退出后再用同一 Token 访问
        resp = client.get("/api/v1/me", headers=headers)
        assert resp.status_code == 401
