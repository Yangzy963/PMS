from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class CommonResponse(BaseModel, Generic[T]):
    """统一响应模型（用于 Swagger 文档展示）"""
    code: int = Field(..., description="业务状态码")
    message: str = Field(..., description="提示信息")
    data: Optional[T] = Field(None, description="业务数据")
