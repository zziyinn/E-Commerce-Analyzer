# 预存数据使用指南

## 📋 概述

当数据库为空时，可以使用预存数据功能快速添加示例产品数据，方便测试和演示。

## 🚀 使用方法

### 方法 1：通过 API 端点（推荐）

部署完成后，访问以下端点预存数据：

```bash
# 使用 curl
curl -X POST https://e-commerce-analyzer-production.up.railway.app/api/seed/sample-products

# 或使用浏览器访问 API 文档
# https://e-commerce-analyzer-production.up.railway.app/docs
# 找到 /api/seed/sample-products 端点，点击 "Try it out" → "Execute"
```

**响应示例：**
```json
{
  "success": true,
  "message": "成功预存 10 个示例产品",
  "run_id": "seed-abc12345-20251129200000",
  "count": 10
}
```

### 方法 2：使用本地脚本

在本地运行脚本预存数据：

```bash
# 确保已设置 MONGODB_URL 环境变量
export MONGODB_URL="mongodb+srv://..."

# 运行脚本
python3 scripts/seed_sample_data.py
```

## 📦 预存的数据内容

预存脚本会创建 **10 个示例产品**，包括：

1. **Men's Classic T-Shirt** - 男士经典 T 恤 ($19.99)
2. **Wireless Bluetooth Earbuds** - 无线蓝牙耳机 ($79.99)
3. **Women's Summer Dress** - 女士夏季连衣裙 ($39.99)
4. **Smart Fitness Tracker** - 智能健身追踪器 ($49.99)
5. **Leather Crossbody Bag** - 真皮斜挎包 ($89.99)
6. **Stainless Steel Water Bottle** - 不锈钢水杯 ($24.99)
7. **Yoga Mat** - 瑜伽垫 ($29.99)
8. **LED Desk Lamp** - LED 台灯 ($34.99)
9. **Portable Phone Charger** - 便携式充电宝 ($39.99)
10. **Organic Coffee Beans** - 有机咖啡豆 ($16.99)

所有产品都包含：
- 产品名称、价格、评分
- 评论数量和评论文本
- 产品描述
- 分类信息
- 平台信息（Amazon）

## ✅ 验证数据

预存数据后，可以通过以下方式验证：

### 1. 通过 API 获取产品列表

```bash
# 获取所有产品
curl https://e-commerce-analyzer-production.up.railway.app/api/products/

# 获取前 5 个产品
curl https://e-commerce-analyzer-production.up.railway.app/api/products/?limit=5

# 按平台筛选
curl https://e-commerce-analyzer-production.up.railway.app/api/products/?platform=amazon
```

### 2. 在前端查看

访问产品搜索页面：
```
https://e-commerce-analyzer-production.up.railway.app/search
```

应该能看到预存的 10 个示例产品。

## 🔄 重复预存

如果数据库中已有数据，再次调用预存端点会：
- 使用 `upsert` 操作（根据 `product_url` 和 `name` 匹配）
- 如果产品已存在，会更新数据
- 如果产品不存在，会创建新记录

**注意：** 预存的数据会标记为 `status: "active"`，可以通过 `/api/products/?status=active` 获取。

## 🛠️ 自定义预存数据

如果需要自定义预存数据，可以修改：

1. **API 端点数据**：编辑 `app/api/seed.py` 中的 `create_sample_products()` 函数
2. **脚本数据**：编辑 `scripts/seed_sample_data.py` 中的 `create_sample_products()` 函数

## 📝 相关文件

- `app/api/seed.py` - API 端点实现
- `scripts/seed_sample_data.py` - 本地脚本实现
- `app/services/mongodb_writer.py` - MongoDB 写入服务
- `app/api/products.py` - 产品 API（用于获取数据）

## ⚠️ 注意事项

1. **MongoDB 连接**：确保 `MONGODB_URL` 环境变量已正确设置
2. **数据格式**：预存的数据必须符合 `ProductWithCategories` schema
3. **状态管理**：预存的数据会自动设置为 `active` 状态
4. **重复数据**：使用 `upsert` 操作，相同 `product_url` 和 `name` 的产品会被更新而不是重复创建

## 🎯 快速开始

1. **部署应用**到 Railway
2. **访问 API 文档**：`https://your-app.railway.app/docs`
3. **找到 `/api/seed/sample-products` 端点**
4. **点击 "Try it out" → "Execute"**
5. **查看响应**，确认数据已预存
6. **访问前端**：`https://your-app.railway.app/search`，应该能看到产品

---

**提示：** 如果前端显示空白，可能是：
1. 数据还未预存（调用预存端点）
2. API 调用失败（检查 CORS 和网络）
3. 前端缓存问题（刷新页面或清除缓存）

