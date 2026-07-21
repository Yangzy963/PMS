"""
测试根配置：将 backend 目录加入 Python 路径
"""
import sys
from pathlib import Path


def _find_project_root() -> Path:
    """向上查找包含 .git 或 backend 目录的目录作为项目根目录，避免硬编码层级。"""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / ".git").exists() or (current / "backend").is_dir():
            return current
        current = current.parent
    # fallback：按已知层级兜底
    return Path(__file__).resolve().parents[1]


backend_dir = _find_project_root() / "backend"
sys.path.insert(0, str(backend_dir))
