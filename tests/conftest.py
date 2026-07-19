"""
测试根配置：将 backend 目录加入 Python 路径
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_dir))
