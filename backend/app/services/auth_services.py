from datetime import timedelta

from app.core.config import settings
from app.core.exceptions import AuthException
from app.schemas.user import TokenResponse, UserLogin
from app.security import create_access_token


def authenticate_user(username: str, password: str) -> bool:
    """
    校验用户名密码
    当前采用硬编码管理员账号，后续可替换为 Redmine 用户验证或数据库验证
    """
    if username != settings.ADMIN_USERNAME:
        return False

    # 临时采用明文比对，生产环境建议改用密码哈希
    if password != settings.ADMIN_PASSWORD:
        return False

    return True


def login(user: UserLogin) -> TokenResponse:
    """用户登录，返回 JWT Token"""
    if not authenticate_user(user.username, user.password):
        raise AuthException("用户名或密码错误")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return TokenResponse(access_token=access_token)
