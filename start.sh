#!/bin/bash
set -e

echo "🚀 Starting deployment process..."

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
  echo "🔧 Activating virtual environment..."
  source venv/bin/activate
fi

# 检查前端是否已构建
if [ ! -d "dist" ] || [ -z "$(ls -A dist)" ]; then
  echo "📦 Building frontend..."
  npm install
  NODE_ENV=production npm run build
else
  echo "✅ Frontend already built, skipping build step"
fi

# 启动后端
echo "🔧 Starting backend API..."
# 确保设置生产环境变量（Railway 会自动设置 PORT，所以这里强制设置为 production）
export ENV=production
echo "✅ ENV set to: $ENV"
echo "✅ PORT: ${PORT:-not set}"
# 使用 python 命令（如果在虚拟环境中，会使用 venv 的 python）
exec python run_api.py

