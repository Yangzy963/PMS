from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录：backend/app/core/config.py -> backend/app/core -> backend/app -> backend -> 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]

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
