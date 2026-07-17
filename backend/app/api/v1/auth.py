from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm

from app.core.exceptions import AuthException
from app.schemas.common import CommonResponse
from app.schemas.user import TokenResponse, UserInfo, UserLogin
from app.security import decode_token
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
    """依赖项：获取当前登录用户"""
    token = credentials.credentials
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise AuthException("Token 无效")
    return UserInfo(username=username)


@router.get("/me", response_model=CommonResponse[UserInfo])
def get_me(current_user: UserInfo = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return success_response(data=current_user)
