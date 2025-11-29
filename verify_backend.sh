#!/bin/bash

# 后端部署验证脚本
# 使用方法: ./verify_backend.sh <your-railway-url>

RAILWAY_URL="${1:-https://e-commerce-analyzer-production.up.railway.app}"

echo "🔍 验证后端部署状态..."
echo "📍 目标地址: $RAILWAY_URL"
echo ""

# 1. 健康检查
echo "1️⃣ 健康检查端点 (/health)"
HEALTH_RESPONSE=$(curl -s -w "\nHTTP状态码: %{http_code}" "$RAILWAY_URL/health")
echo "$HEALTH_RESPONSE"
echo ""

# 2. API 根路径
echo "2️⃣ API 根路径 (/)"
ROOT_RESPONSE=$(curl -s -w "\nHTTP状态码: %{http_code}" "$RAILWAY_URL/")
echo "$ROOT_RESPONSE"
echo ""

# 3. API 文档
echo "3️⃣ API 文档 (/docs)"
DOCS_STATUS=$(curl -s -o /dev/null -w "HTTP状态码: %{http_code}" "$RAILWAY_URL/docs")
echo "$DOCS_STATUS"
echo ""

# 4. 产品列表 API
echo "4️⃣ 产品列表 API (/api/products/)"
PRODUCTS_RESPONSE=$(curl -s -w "\nHTTP状态码: %{http_code}" "$RAILWAY_URL/api/products/")
echo "$PRODUCTS_RESPONSE" | head -20
echo ""

# 5. 检查响应时间
echo "5️⃣ 响应时间测试"
RESPONSE_TIME=$(curl -s -o /dev/null -w "响应时间: %{time_total}秒" "$RAILWAY_URL/health")
echo "$RESPONSE_TIME"
echo ""

echo "✅ 验证完成！"
echo ""
echo "💡 提示："
echo "   - 如果所有端点返回 200，说明后端正常运行"
echo "   - 如果返回 404，可能是路由配置问题"
echo "   - 如果返回 500，检查 Railway 日志"

