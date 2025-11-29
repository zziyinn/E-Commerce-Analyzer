#!/bin/bash

# 系统化问题排查脚本
# 逐步验证每个环节，定位问题

RAILWAY_URL="https://e-commerce-analyzer-production.up.railway.app"

echo "🔍 开始系统化排查..."
echo ""

# 步骤 1: 检查健康状态
echo "=== 步骤 1: 检查后端健康状态 ==="
HEALTH=$(curl -s "$RAILWAY_URL/health")
echo "健康检查响应: $HEALTH"
if [[ "$HEALTH" == *"ok"* ]]; then
  echo "✅ 后端服务正常运行"
else
  echo "❌ 后端服务异常"
fi
echo ""

# 步骤 2: 检查 API 端点
echo "=== 步骤 2: 检查产品 API 端点 ==="
PRODUCTS_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$RAILWAY_URL/api/products/?limit=1")
HTTP_CODE=$(echo "$PRODUCTS_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$PRODUCTS_RESPONSE" | sed '/HTTP_CODE/d')
echo "HTTP 状态码: $HTTP_CODE"
echo "响应内容: $BODY" | head -5
if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ API 端点正常"
else
  echo "❌ API 端点异常 (状态码: $HTTP_CODE)"
fi
echo ""

# 步骤 3: 检查 CORS 头
echo "=== 步骤 3: 检查 CORS 配置 ==="
CORS_HEADERS=$(curl -s -I -X OPTIONS "$RAILWAY_URL/api/products/" \
  -H "Origin: https://e-commerce-analyzer-production.up.railway.app" \
  -H "Access-Control-Request-Method: GET" | grep -i "access-control")
echo "CORS 响应头:"
echo "$CORS_HEADERS"
if [[ "$CORS_HEADERS" == *"Access-Control-Allow-Origin"* ]]; then
  echo "✅ CORS 配置正常"
else
  echo "⚠️  CORS 配置可能有问题"
fi
echo ""

# 步骤 4: 检查静态文件
echo "=== 步骤 4: 检查静态文件服务 ==="
STATIC_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/assets/index-DTWxAghn.css")
if [ "$STATIC_CHECK" = "200" ]; then
  echo "✅ 静态文件服务正常"
else
  echo "❌ 静态文件服务异常 (状态码: $STATIC_CHECK)"
fi
echo ""

# 步骤 5: 检查前端页面
echo "=== 步骤 5: 检查前端页面 ==="
PAGE_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/search")
if [ "$PAGE_CHECK" = "200" ]; then
  echo "✅ 前端页面正常 (状态码: $PAGE_CHECK)"
else
  echo "❌ 前端页面异常 (状态码: $PAGE_CHECK)"
fi
echo ""

# 步骤 6: 检查预存数据端点
echo "=== 步骤 6: 检查预存数据端点 ==="
SEED_CHECK=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$RAILWAY_URL/api/seed/sample-products")
if [ "$SEED_CHECK" = "200" ] || [ "$SEED_CHECK" = "405" ]; then
  echo "✅ 预存数据端点可访问 (状态码: $SEED_CHECK)"
else
  echo "⚠️  预存数据端点状态码: $SEED_CHECK"
fi
echo ""

# 步骤 7: 检查构建产物中的 API_BASE_URL
echo "=== 步骤 7: 检查构建产物 ==="
echo "检查构建后的 JS 文件中是否包含 localhost:8000..."
# 注意：这个检查需要访问实际的构建文件
echo "⚠️  需要在浏览器中检查构建后的 JS 文件"
echo ""

echo "📋 排查完成！"
echo ""
echo "💡 下一步："
echo "1. 在浏览器中打开: $RAILWAY_URL/search"
echo "2. 打开开发者工具 (F12)"
echo "3. 查看 Console 标签页中的日志"
echo "4. 查看 Network 标签页中的 API 请求"
echo "5. 检查 [ProductService] Environment 日志中的 API_BASE_URL 值"

