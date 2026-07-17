class AppException(Exception):
    """业务异常基类"""

    def __init__(self, message: str = "业务异常", code: int = 400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message=message, code=404)


class AuthException(AppException):
    def __init__(self, message: str = "认证失败"):
        super().__init__(message=message, code=401)


class PermissionException(AppException):
    def __init__(self, message: str = "无权访问"):
        super().__init__(message=message, code=403)


class ValidationException(AppException):
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(message=message, code=422)


class RedmineException(AppException):
    def __init__(self, message: str = "Redmine 服务异常"):
        super().__init__(message=message, code=502)
