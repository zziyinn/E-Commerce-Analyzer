#!/bin/bash
set -e

echo "🚀 Starting deployment process..."

# 检查前端是否已构建
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
  echo "📦 Building frontend..."
  npm install
  npm run build
else
  echo "✅ Frontend already built, skipping build step"
fi

# 启动后端
echo "🔧 Starting backend API..."
# 设置生产环境变量
export ENV=${ENV:-production}
exec python run_api.py

