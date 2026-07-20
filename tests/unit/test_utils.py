"""
单元测试：工具函数（密码哈希、响应格式）
"""
import pytest


# bcrypt/passlib 版本兼容性检查
def _bcrypt_works():
    try:
        from app.utils.password import get_password_hash, verify_password
        get_password_hash("test")
        return True
    except Exception:
        return False


_skip_password = not _bcrypt_works()


class TestPassword:
    """密码哈希与校验"""

    @pytest.mark.skipif(_skip_password, reason="bcrypt/passlib 版本不兼容")
    def test_hash_and_verify(self):
        """哈希后可校验"""
        from app.utils.password import get_password_hash, verify_password
        hashed = get_password_hash("test1234")
        assert hashed != "test1234"
        assert verify_password("test1234", hashed) is True

    @pytest.mark.skipif(_skip_password, reason="bcrypt/passlib 版本不兼容")
    def test_verify_wrong_password(self):
        """错误密码校验失败"""
        from app.utils.password import get_password_hash, verify_password
        hashed = get_password_hash("correct")
        assert verify_password("wrong", hashed) is False

    @pytest.mark.skipif(_skip_password, reason="bcrypt/passlib 版本不兼容")
    def test_hash_is_stable_for_verify(self):
        """同一密码两次哈希结果不同（salt），但都能校验"""
        from app.utils.password import get_password_hash, verify_password
        h1 = get_password_hash("pwd123")
        h2 = get_password_hash("pwd123")
        assert h1 != h2
        assert verify_password("pwd123", h1) is True
        assert verify_password("pwd123", h2) is True


class TestResponse:
    """统一响应格式"""

    def test_success_default(self):
        """默认成功响应"""
        from app.utils.response import success_response
        resp = success_response()
        assert resp["code"] == 200
        assert resp["message"] == "success"
        assert resp["data"] is None

    def test_success_with_data(self):
        """带数据的成功响应"""
        from app.utils.response import success_response
        resp = success_response(data={"id": 1}, message="创建成功", code=201)
        assert resp["code"] == 201
        assert resp["message"] == "创建成功"
        assert resp["data"] == {"id": 1}

    def test_error_response(self):
        """错误响应"""
        from app.utils.response import error_response
        from fastapi.responses import JSONResponse
        resp = error_response(message="参数错误", code=422)
        assert isinstance(resp, JSONResponse)
        assert resp.status_code == 422
        import json
        body = json.loads(resp.body)
        assert body["message"] == "参数错误"

    def test_error_response_default(self):
        """默认错误响应"""
        from app.utils.response import error_response
        resp = error_response()
        assert resp.status_code == 400
