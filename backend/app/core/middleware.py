from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.utils.response import error_response


async def app_exception_handler(request: Request, exc: AppException):
    """全局业务异常处理"""
    return error_response(message=exc.message, code=exc.code)


async def generic_exception_handler(request: Request, exc: Exception):
    """全局未知异常处理"""
    return error_response(message=f"服务器内部错误: {str(exc)}", code=500)


def register_exception_handlers(app):
    """注册异常处理器"""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
