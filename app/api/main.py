"""
FastAPI 應用主入口
"""

import os
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import products, scrape, analysis

app = FastAPI(
    title="Amazon Products API",
    description="產品數據 API",
    version="1.0.0",
)

# 获取环境变量，判断是否为生产环境
# Railway 环境：如果 ENV 未设置，但 PORT 已设置（Railway 自动设置），则认为是生产环境
env_value = os.getenv("ENV", "")
port_value = os.getenv("PORT", "")
is_production = env_value == "production" or (env_value == "" and port_value != "")
railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")

# CORS 配置
cors_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3003",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3003",
]

# 生产环境添加 Railway 域名
if is_production and railway_public_domain:
    cors_origins.extend([
        f"https://{railway_public_domain}",
        f"http://{railway_public_domain}",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由（API 路由优先注册，确保优先匹配）
app.include_router(products.router)
app.include_router(scrape.router)
app.include_router(analysis.router)

# 生产环境：提供静态文件服务
if is_production:
    dist_path = Path(__file__).parent.parent.parent / "dist"
    print(f"[DEBUG] is_production: {is_production}, dist_path: {dist_path}, exists: {dist_path.exists()}")
    if dist_path.exists():
        # 挂载静态文件（必须在 SPA 路由之前）
        assets_path = dist_path / "assets"
        if assets_path.exists():
            app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
            print(f"[DEBUG] Mounted /assets from {assets_path}")
        
        # 提供 index.html 用于前端路由（放在最后，作为 fallback）
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            """提供 SPA 支持，所有非 API 路由返回 index.html"""
            # 排除 API 路由和文档路由
            if (full_path.startswith("api/") or 
                full_path.startswith("docs") or 
                full_path.startswith("openapi.json") or
                full_path == "health" or
                full_path == "favicon.ico"):
                return Response(status_code=404)
            
            # 如果是静态资源，已经由上面的 mount 处理
            if full_path.startswith("assets/"):
                return Response(status_code=404)
            
            # 返回 index.html
            index_file = dist_path / "index.html"
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    return Response(content=f.read(), media_type="text/html")
            print(f"[DEBUG] index.html not found at {index_file}")
            return Response(status_code=404)
    else:
        print(f"[WARNING] dist directory not found at {dist_path}")


@app.get("/")
def root():
    # 生产环境返回前端页面，开发环境返回 API 信息
    if is_production:
        dist_path = Path(__file__).parent.parent.parent / "dist"
        index_file = dist_path / "index.html"
        print(f"[DEBUG] Root path - is_production: {is_production}, index_file: {index_file}, exists: {index_file.exists()}")
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                return Response(content=f.read(), media_type="text/html")
        else:
            print(f"[WARNING] index.html not found at {index_file}, dist_path exists: {dist_path.exists()}")
    return {"message": "Amazon Products API", "version": "1.0.0", "is_production": is_production, "dist_exists": (Path(__file__).parent.parent.parent / "dist").exists()}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/favicon.ico")
def favicon():
    """处理 favicon 请求，避免 404 错误"""
    return Response(status_code=204)

