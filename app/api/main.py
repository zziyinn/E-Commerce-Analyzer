"""
FastAPI 應用主入口
"""

import os
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import products, scrape, analysis, seed

app = FastAPI(
    title="Amazon Products API",
    description="產品數據 API",
    version="1.0.0",
)

# 获取环境变量，判断是否为生产环境
# Railway 环境：如果 PORT 已设置（Railway 自动设置），则认为是生产环境
# 或者 ENV 明确设置为 "production"
env_value = os.getenv("ENV", "").lower()
port_value = os.getenv("PORT", "")
# 如果 PORT 存在（Railway 自动设置），或者 ENV=production，则认为是生产环境
is_production = port_value != "" or env_value == "production"
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

# 生产环境：允许所有来源（因为前后端同域，但为了安全也可以只允许特定域名）
if is_production:
    # 添加 Railway 域名
    if railway_public_domain:
        cors_origins.extend([
            f"https://{railway_public_domain}",
            f"http://{railway_public_domain}",
        ])
    # 生产环境允许所有来源（前后端同域，通常不需要 CORS，但为了兼容性保留）
    # 如果前后端确实同域，可以设置为 ["*"] 或只允许 Railway 域名
    cors_origins.append("*")  # 允许所有来源（生产环境前后端同域，通常不需要）

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if not is_production else ["*"],  # 生产环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由（API 路由优先注册，确保优先匹配）
app.include_router(products.router)
app.include_router(scrape.router)
app.include_router(analysis.router)
app.include_router(seed.router)

# 注册特定路由（必须在 SPA 路由之前）
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/favicon.ico")
def favicon():
    """处理 favicon 请求，避免 404 错误"""
    return Response(status_code=204)


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
        
        # 根路径：返回 index.html
        @app.get("/")
        def root():
            """根路径返回前端页面"""
            index_file = dist_path / "index.html"
            print(f"[DEBUG] Root path - index_file: {index_file}, exists: {index_file.exists()}")
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    return Response(content=f.read(), media_type="text/html")
            else:
                print(f"[WARNING] index.html not found at {index_file}, dist_path exists: {dist_path.exists()}")
                return {"message": "Amazon Products API", "version": "1.0.0", "is_production": True, "dist_exists": False}
        
        # SPA 路由：所有其他路径返回 index.html（必须在最后注册）
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
            
            # 返回 index.html（Vue Router 会处理客户端路由）
            index_file = dist_path / "index.html"
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    return Response(content=f.read(), media_type="text/html")
            print(f"[DEBUG] index.html not found at {index_file}")
            return Response(status_code=404)
    else:
        print(f"[WARNING] dist directory not found at {dist_path}")


# 开发环境：根路径返回 API 信息
if not is_production:
    @app.get("/")
    def root():
        return {"message": "Amazon Products API", "version": "1.0.0", "is_production": False, "dist_exists": (Path(__file__).parent.parent.parent / "dist").exists()}

