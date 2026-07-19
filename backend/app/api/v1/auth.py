from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm

from app.core.exceptions import AuthException
from app.redis import blacklist_token, is_token_blacklisted
from app.schemas.common import CommonResponse
from app.schemas.user import TokenResponse, UserInfo, UserLogin
from app.security import create_access_token, decode_token
from app.core.config import settings
from app.services.auth_services import login
from app.utils.response import success_response

router = APIRouter(tags=["认证"])

# 使用 HTTPBearer，Swagger 会显示简单的 Token 输入框
security_scheme = HTTPBearer()


@router.post("/login", response_model=CommonResponse[TokenResponse])
def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录接口"""
    user = UserLogin(username=form_data.username, password=form_data.password)
    token = login(user)
    return success_response(data=token, message="登录成功")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> UserInfo:
    """依赖项：获取当前登录用户（含黑名单检查）"""
    token = credentials.credentials

    # 检查 Token 是否已被退出登录拉黑
    if is_token_blacklisted(token):
        raise AuthException("Token 已失效，请重新登录")

    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise AuthException("Token 无效")
    return UserInfo(username=username)


@router.post("/logout", response_model=CommonResponse[dict])
def user_logout(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
):
    """退出登录，将当前 Token 加入黑名单"""
    token = credentials.credentials

    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        if exp:
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = max(exp - now, 1)
            blacklist_token(token, ttl)
    except AuthException:
        pass

    return success_response(data={}, message="退出成功")


@router.get("/me", response_model=CommonResponse[UserInfo])
def get_me(current_user: UserInfo = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return success_response(data=current_user)
