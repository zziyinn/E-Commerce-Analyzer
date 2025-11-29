#!/bin/bash

# 本地测试脚本
# 用于测试前后端是否正常工作

echo "🚀 开始本地测试..."
echo ""

# 检查后端是否运行
echo "1. 检查后端 API..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端 API 运行正常"
else
    echo "❌ 后端 API 未运行，请先启动后端："
    echo "   python run_api.py"
    exit 1
fi

# 检查前端是否运行
echo ""
echo "2. 检查前端..."
if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ 前端运行正常"
else
    echo "⚠️  前端未运行，请启动前端："
    echo "   npm run dev"
fi

# 测试 API 端点
echo ""
echo "3. 测试 API 端点..."

# 测试健康检查
echo "   - /health"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$response" = "200" ]; then
    echo "     ✅ 健康检查通过"
else
    echo "     ❌ 健康检查失败 (HTTP $response)"
fi

# 测试产品列表
echo "   - /api/products/"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/products/)
if [ "$response" = "200" ]; then
    echo "     ✅ 产品列表 API 正常"
    product_count=$(curl -s http://localhost:8000/api/products/ | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data) if isinstance(data, list) else 0)" 2>/dev/null || echo "0")
    echo "     📦 产品数量: $product_count"
else
    echo "     ❌ 产品列表 API 失败 (HTTP $response)"
fi

# 测试分析 API（即使返回空数据也应该返回 200）
echo "   - /api/analysis/price-trend"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/analysis/price-trend)
if [ "$response" = "200" ]; then
    echo "     ✅ 价格趋势 API 正常"
else
    echo "     ❌ 价格趋势 API 失败 (HTTP $response)"
fi

echo "   - /api/analysis/category-distribution"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/analysis/category-distribution)
if [ "$response" = "200" ]; then
    echo "     ✅ 分类分布 API 正常"
else
    echo "     ❌ 分类分布 API 失败 (HTTP $response)"
fi

echo "   - /api/analysis/competition-analysis"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/analysis/competition-analysis)
if [ "$response" = "200" ]; then
    echo "     ✅ 竞争分析 API 正常"
else
    echo "     ❌ 竞争分析 API 失败 (HTTP $response)"
fi

# 测试数据质量
echo "   - /api/analysis/data-quality"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/analysis/data-quality)
if [ "$response" = "200" ]; then
    echo "     ✅ 数据质量 API 正常"
else
    echo "     ❌ 数据质量 API 失败 (HTTP $response)"
fi

echo ""
echo "📝 测试完成！"
echo ""
echo "如果所有 API 都返回 200，但前端仍然显示错误，请检查："
echo "  1. 浏览器控制台的错误信息"
echo "  2. 前端是否正确连接到 http://localhost:8000"
echo "  3. 数据库是否有数据（如果没有，可以调用 /api/seed/sample-products）"

