from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_project_root() -> Path:
    """向上查找包含 .env 或 .git 的目录作为项目根目录，避免硬编码层级。"""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / ".env").exists() or (current / ".git").exists():
            return current
        current = current.parent
    # fallback：按已知层级兜底
    return Path(__file__).resolve().parents[3]


PROJECT_ROOT = _find_project_root()

class Settings(BaseSettings):
    """应用配置，优先从环境变量读取，其次从项目根目录的 .env 文件读取"""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Redmine 配置
    REDMINE_BASE_URL: str = "http://127.0.0.1:3000"
    REDMINE_API_KEY: str = ""
    REDMINE_PROJECT_KEY: str = "pms"
    REDMINE_TRACKER_NAME: str = "人员信息"

    # 应用配置
    APP_NAME: str = "人员信息管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 天
    ALGORITHM: str = "HS256"

    # 管理员账号（临时硬编码登录）
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # Redis 配置（可选）
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0


settings = Settings()
