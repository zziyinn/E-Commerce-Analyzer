#!/usr/bin/env python3
"""
啟動 FastAPI 服務器
用法: python run_api.py
"""

import os
import uvicorn
from app.api.main import app

if __name__ == "__main__":
    # Railway 会提供 PORT 环境变量
    port = int(os.getenv("PORT", 8000))
    # 生产环境禁用 reload
    reload = os.getenv("ENV", "production") != "production"
    
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_level="info",
    )

