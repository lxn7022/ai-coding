"""pytest 配置：在项目目录下创建临时目录。"""
import shutil
import uuid
from pathlib import Path

import pytest


@pytest.fixture
def tmp_path():
    """使用项目目录下的临时目录（与 pytest 默认 tmp_path 行为一致）。"""
    project_root = Path(__file__).resolve().parent
    base = project_root / ".pytest_tmp"
    base.mkdir(parents=True, exist_ok=True)
    path = base / str(uuid.uuid4())[:8]
    path.mkdir(parents=True, exist_ok=True)
    yield path
    try:
        shutil.rmtree(path, ignore_errors=True)
    except OSError:
        pass
