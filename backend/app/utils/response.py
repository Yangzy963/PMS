from typing import Any, Optional

from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200,
) -> dict:
    """统一成功响应格式"""
    return {
        "code": code,
        "message": message,
        "data": data,
    }


def error_response(
    message: str = "error",
    code: int = 400,
    data: Optional[Any] = None,
) -> JSONResponse:
    """统一错误响应格式"""
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "message": message,
            "data": data,
        },
    )
