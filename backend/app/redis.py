"""
Redis 客户端封装，用于 Token 黑名单等缓存操作
"""
from typing import Optional

import redis

from app.core.config import settings

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """获取 Redis 客户端（单例）"""
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        _redis_client.ping()
    except Exception:
        _redis_client = None

    return _redis_client


def blacklist_token(token: str, ttl_seconds: int) -> bool:
    """
    将 Token 加入黑名单
    """
    client = get_redis_client()
    if client is None:
        return False

    key = f"blacklist:token:{token}"
    client.set(key, "1", ex=ttl_seconds)
    return True


def is_token_blacklisted(token: str) -> bool:
    """
    检查 Token 是否在黑名单中
    """
    client = get_redis_client()
    if client is None:
        return False

    key = f"blacklist:token:{token}"
    return client.exists(key) > 0
