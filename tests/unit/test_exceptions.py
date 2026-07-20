"""
单元测试：自定义异常类
"""


class TestAppException:
    """基础业务异常"""

    def test_default_values(self):
        from app.core.exceptions import AppException
        ex = AppException()
        assert ex.message == "业务异常"
        assert ex.code == 400
        assert str(ex) == "业务异常"

    def test_custom_message(self):
        from app.core.exceptions import AppException
        ex = AppException(message="自定义错误", code=500)
        assert ex.message == "自定义错误"
        assert ex.code == 500
        assert str(ex) == "自定义错误"


class TestNotFoundException:
    """资源不存在异常"""

    def test_default(self):
        from app.core.exceptions import NotFoundException
        ex = NotFoundException()
        assert ex.code == 404
        assert "资源不存在" in ex.message

    def test_custom(self):
        from app.core.exceptions import NotFoundException
        ex = NotFoundException(message="用户 123 不存在")
        assert ex.code == 404
        assert ex.message == "用户 123 不存在"


class TestAuthException:
    """认证异常"""

    def test_default(self):
        from app.core.exceptions import AuthException
        ex = AuthException()
        assert ex.code == 401
        assert "认证失败" in ex.message

    def test_custom(self):
        from app.core.exceptions import AuthException
        ex = AuthException(message="Token 已过期")
        assert ex.code == 401
        assert ex.message == "Token 已过期"


class TestPermissionException:
    """权限异常"""

    def test_default(self):
        from app.core.exceptions import PermissionException
        ex = PermissionException()
        assert ex.code == 403

    def test_custom(self):
        from app.core.exceptions import PermissionException
        ex = PermissionException(message="无权删除")
        assert ex.code == 403


class TestValidationException:
    """校验异常"""

    def test_default(self):
        from app.core.exceptions import ValidationException
        ex = ValidationException()
        assert ex.code == 422

    def test_custom(self):
        from app.core.exceptions import ValidationException
        ex = ValidationException(message="年龄超出范围")
        assert ex.code == 422


class TestRedmineException:
    """Redmine 异常"""

    def test_default(self):
        from app.core.exceptions import RedmineException
        ex = RedmineException()
        assert ex.code == 502

    def test_custom(self):
        from app.core.exceptions import RedmineException
        ex = RedmineException(message="连接超时")
        assert ex.code == 502

    def test_is_app_exception(self):
        """所有异常都是 AppException 的子类"""
        from app.core.exceptions import (
            AppException, NotFoundException, AuthException,
            PermissionException, ValidationException, RedmineException,
        )
        for cls in [NotFoundException, AuthException, PermissionException,
                     ValidationException, RedmineException]:
            assert issubclass(cls, AppException)
