#!/usr/bin/env python3
"""
乒乓球培训管理系统后端启动脚本

使用uv运行:
uv run python backend/run.py

或者使用项目脚本:
uv run dev  # 开发模式
uv run start  # 生产模式
"""

import uvicorn
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
