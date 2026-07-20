"""
单元测试：认证服务（authenticate_user / login）
"""
import pytest
from unittest.mock import patch


class TestAuthenticateUser:
    """用户名密码校验"""

    def test_correct_credentials(self, monkeypatch):
        """正确用户名密码"""
        monkeypatch.setattr("app.core.config.settings.ADMIN_USERNAME", "admin")
        monkeypatch.setattr("app.core.config.settings.ADMIN_PASSWORD", "admin123")
        from app.services.auth_services import authenticate_user
        assert authenticate_user("admin", "admin123") is True

    def test_wrong_username(self, monkeypatch):
        """用户名错误"""
        monkeypatch.setattr("app.core.config.settings.ADMIN_USERNAME", "admin")
        monkeypatch.setattr("app.core.config.settings.ADMIN_PASSWORD", "admin123")
        from app.services.auth_services import authenticate_user
        assert authenticate_user("wrong_user", "admin123") is False

    def test_wrong_password(self, monkeypatch):
        """密码错误"""
        monkeypatch.setattr("app.core.config.settings.ADMIN_USERNAME", "admin")
        monkeypatch.setattr("app.core.config.settings.ADMIN_PASSWORD", "admin123")
        from app.services.auth_services import authenticate_user
        assert authenticate_user("admin", "wrong_pwd") is False

    def test_both_wrong(self, monkeypatch):
        """用户名密码均错误"""
        monkeypatch.setattr("app.core.config.settings.ADMIN_USERNAME", "admin")
        monkeypatch.setattr("app.core.config.settings.ADMIN_PASSWORD", "admin123")
        from app.services.auth_services import authenticate_user
        assert authenticate_user("x", "y") is False


class TestLogin:
    """登录生成 Token"""

    def test_login_success(self, monkeypatch):
        """登录成功返回 TokenResponse"""
        monkeypatch.setattr("app.core.config.settings.ADMIN_USERNAME", "admin")
        monkeypatch.setattr("app.core.config.settings.ADMIN_PASSWORD", "admin123")
        monkeypatch.setattr("app.core.config.settings.SECRET_KEY", "test-secret")
        monkeypatch.setattr("app.core.config.settings.ACCESS_TOKEN_EXPIRE_MINUTES", 30)
        from app.schemas.user import UserLogin
        from app.services.auth_services import login
        user = UserLogin(username="admin", password="admin123")
        result = login(user)
        assert result.access_token is not None
        assert len(result.access_token) > 0
        assert result.token_type == "bearer"

    def test_login_failure(self, monkeypatch):
        """登录失败抛出 AuthException"""
        monkeypatch.setattr("app.core.config.settings.ADMIN_USERNAME", "admin")
        monkeypatch.setattr("app.core.config.settings.ADMIN_PASSWORD", "admin123")
        from app.schemas.user import UserLogin
        from app.services.auth_services import login
        from app.core.exceptions import AuthException
        user = UserLogin(username="admin", password="wrong")
        with pytest.raises(AuthException, match="用户名或密码错误"):
            login(user)


class TestGetCurrentUser:
    """Token 解析获取当前用户"""

    def test_token_with_empty_sub_raises(self, monkeypatch):
        """Token payload 中无 sub → AuthException (auth.py:42)"""
        monkeypatch.setattr("app.api.v1.auth.is_token_blacklisted", lambda t: False)
        monkeypatch.setattr(
            "app.api.v1.auth.decode_token",
            lambda t: {"exp": 9999999999, "jti": "test"},
        )
        from app.api.v1.auth import get_current_user
        from app.core.exceptions import AuthException
        import asyncio
        from unittest.mock import MagicMock

        # get_current_user 接收 HTTPAuthorizationCredentials，不是裸字符串
        creds = MagicMock()
        creds.credentials = "fake-token"

        async def run():
            try:
                await get_current_user(creds)
                assert False, "应该抛出异常"
            except AuthException as e:
                assert "无效" in str(e)

        asyncio.run(run())
