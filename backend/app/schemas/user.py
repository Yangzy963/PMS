from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, max_length=100, description="密码")


class TokenResponse(BaseModel):
    """登录成功响应"""
    access_token: str = Field(..., description="JWT Token")
    token_type: str = Field("bearer", description="Token 类型")


class UserInfo(BaseModel):
    """当前登录用户信息"""
    username: str = Field(..., description="用户名")
