# Railway 环境变量完整配置指南

## 📋 所有可用环境变量列表

### 🔴 必需变量（必须设置）

| 变量名 | 值 | 说明 | 示例 |
|--------|-----|------|------|
| `MONGODB_URL` | MongoDB 连接字符串 | MongoDB Atlas 连接 URL | `mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority` |
| `MONGODB_DATABASE` | 数据库名称 | MongoDB 数据库名 | `amazon_products` |
| `ENV` | `production` | 环境类型（必须为 production） | `production` |

### 🟡 前端变量

| 变量名 | 值 | 说明 | 默认值 |
|--------|-----|------|--------|
| `VITE_API_BASE_URL` | API 基础 URL | 留空使用相对路径（推荐） | (留空) |
| `VITE_FLAG_EMPTY_WARM_CARD` | `true`/`false` | 启用空状态提示卡片 | `true` |

### 🟢 后端核心配置

| 变量名 | 值 | 说明 | 默认值 |
|--------|-----|------|--------|
| `LOG_LEVEL` | `DEBUG`/`INFO`/`WARNING`/`ERROR` | 日志级别 | `INFO` |
| `DATABASE_URL` | PostgreSQL 连接字符串 | PostgreSQL 数据库（可选，项目主要用 MongoDB） | `postgresql+psycopg://user:pass@localhost:5432/db` |
| `FIRECRAWL_API_KEY` | Firecrawl API 密钥 | Firecrawl 服务密钥（如果使用） | (留空) |

### 🔵 AI 分析功能

| 变量名 | 值 | 说明 | 默认值 |
|--------|-----|------|--------|
| `GOOGLE_AI_API_KEY` | Google AI API 密钥 | Google Gemini API 密钥（用于 AI 分析） | (留空) |

### 🟣 爬虫配置

| 变量名 | 值 | 说明 | 默认值 |
|--------|-----|------|--------|
| `MAX_PRODUCTS_PER_SEARCH` | 数字 | 每次搜索最大产品数 | `20` |
| `DELAY_MIN` | 浮点数（秒） | 爬虫延迟最小值 | `2.0` |
| `DELAY_MAX` | 浮点数（秒） | 爬虫延迟最大值 | `5.0` |
| `HEADLESS` | `true`/`false` | 无头浏览器模式 | `true` |
| `ENABLE_REQUEST_MONITORING` | `true`/`false` | 启用请求监控 | `true` |
| `PROXY` | 代理地址 | 代理服务器（格式: `http://user:pass@host:port` 或 `socks5://host:port`） | (留空) |
| `COOKIES_FILE` | 文件路径 | Cookies 文件路径 | `data/cookies.json` |
| `OUTPUT_DIR` | 目录路径 | 爬取内容输出目录 | `data/scraped_content` |
| `LOG_FILE` | 文件路径 | 日志文件路径 | `data/logs/scraper.log` |

### ⚪ Railway 自动设置（无需手动添加）

以下变量由 Railway 自动设置，无需手动配置：

- `PORT` - Railway 自动提供端口号
- `RAILWAY_PUBLIC_DOMAIN` - Railway 自动提供公共域名（部署后）
- `RAILWAY_ENVIRONMENT` - Railway 环境名称
- `RAILWAY_PROJECT_ID` - Railway 项目 ID
- `RAILWAY_SERVICE_ID` - Railway 服务 ID

---

## 📝 快速配置模板

### 最小配置（必需变量）

```bash
MONGODB_URL=mongodb+srv://Ziyinzx_db_user:qihTWbIOb3HHvj22@cluster0.y0kykwv.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=amazon_products
ENV=production
VITE_API_BASE_URL=
```

### 标准配置（推荐）

```bash
# 必需变量
MONGODB_URL=mongodb+srv://Ziyinzx_db_user:qihTWbIOb3HHvj22@cluster0.y0kykwv.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=amazon_products
ENV=production

# 前端配置
VITE_API_BASE_URL=

# 日志配置
LOG_LEVEL=INFO

# 爬虫配置
MAX_PRODUCTS_PER_SEARCH=20
DELAY_MIN=2.0
DELAY_MAX=5.0
HEADLESS=true
ENABLE_REQUEST_MONITORING=true
```

### 完整配置（包含所有功能）

```bash
# ========== 必需变量 ==========
MONGODB_URL=mongodb+srv://Ziyinzx_db_user:qihTWbIOb3HHvj22@cluster0.y0kykwv.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=amazon_products
ENV=production

# ========== 前端配置 ==========
VITE_API_BASE_URL=
VITE_FLAG_EMPTY_WARM_CARD=true

# ========== 后端核心配置 ==========
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/testdb
FIRECRAWL_API_KEY=fc-temp-key

# ========== AI 分析功能 ==========
GOOGLE_AI_API_KEY=你的_google_ai_api_key_在这里

# ========== 爬虫配置 ==========
MAX_PRODUCTS_PER_SEARCH=20
DELAY_MIN=2.0
DELAY_MAX=5.0
HEADLESS=true
ENABLE_REQUEST_MONITORING=true
PROXY=
COOKIES_FILE=data/cookies.json
OUTPUT_DIR=data/scraped_content
LOG_FILE=data/logs/scraper.log
```

### 生产环境推荐配置

```bash
# ========== 必需变量 ==========
MONGODB_URL=mongodb+srv://Ziyinzx_db_user:qihTWbIOb3HHvj22@cluster0.y0kykwv.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=amazon_products
ENV=production

# ========== 前端配置 ==========
VITE_API_BASE_URL=

# ========== 日志配置 ==========
LOG_LEVEL=INFO

# ========== 爬虫配置（生产环境优化） ==========
MAX_PRODUCTS_PER_SEARCH=20
DELAY_MIN=3.0
DELAY_MAX=6.0
HEADLESS=true
ENABLE_REQUEST_MONITORING=true

# ========== AI 分析功能（可选） ==========
# GOOGLE_AI_API_KEY=你的_google_ai_api_key_在这里
```

---

## 🚀 在 Railway 中设置步骤

### 方法 1：通过 Railway Dashboard（推荐）

1. 登录 Railway Dashboard: https://railway.app
2. 选择你的项目：`E-Commerce-Analyzer`
3. 点击项目名称进入项目设置
4. 点击 **"Variables"** 标签
5. 点击 **"New Variable"** 添加每个变量
6. 输入变量名和值
7. 点击 **"Add"** 保存
8. 重复步骤 5-7 添加所有变量

### 方法 2：通过 Railway CLI（批量导入）

```bash
# 安装 Railway CLI
npm i -g @railway/cli

# 登录
railway login

# 链接项目
railway link

# 批量设置变量（从文件）
railway variables set MONGODB_URL="mongodb+srv://..." MONGODB_DATABASE="amazon_products" ENV="production"
```

### 方法 3：使用 Railway API

```bash
# 获取 API token 从 Railway Dashboard → Settings → Tokens
RAILWAY_TOKEN=your_token_here
PROJECT_ID=your_project_id

# 设置变量
curl -X POST "https://api.railway.app/v1/projects/$PROJECT_ID/variables" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MONGODB_URL",
    "value": "mongodb+srv://..."
  }'
```

---

## ✅ 验证配置

### 1. 检查环境变量是否加载

部署后，在 Railway 日志中查看：

```bash
# 在 Railway Dashboard → Deployments → View Logs
# 应该看到类似输出：
# ✅ ENV set to: production
# ✅ PORT: 8080
```

### 2. 测试 API 端点

```bash
# 健康检查
curl https://e-commerce-analyzer-production.up.railway.app/health

# 产品列表（应该返回数据或空数组）
curl https://e-commerce-analyzer-production.up.railway.app/api/products/

# API 文档
open https://e-commerce-analyzer-production.up.railway.app/docs
```

### 3. 使用验证脚本

```bash
./verify_backend.sh https://e-commerce-analyzer-production.up.railway.app
```

---

## ⚠️ 重要注意事项

### 1. 敏感信息保护

- **MONGODB_URL** 包含密码，确保在 Railway 中设置为 **Secret**（Railway 会自动处理）
- **GOOGLE_AI_API_KEY** 是敏感信息，不要提交到 Git
- 所有包含密码、密钥的变量都应该在 Railway 中设置为 Secret

### 2. URL 编码

如果 `MONGODB_URL` 中的密码包含特殊字符，需要进行 URL 编码：

```bash
# 特殊字符编码表
# @ → %40
# : → %3A
# / → %2F
# ? → %3F
# & → %26
# = → %3D
# # → %23
```

### 3. 环境变量优先级

1. Railway 环境变量（最高优先级）
2. `.env` 文件（本地开发）
3. 代码中的默认值（最低优先级）

### 4. 前端变量命名

- 所有前端环境变量必须以 `VITE_` 开头
- 只有 `VITE_` 开头的变量才会在构建时注入到前端代码中
- 修改前端变量后需要重新构建

### 5. 布尔值处理

- Railway 中的布尔值应该使用字符串：`"true"` 或 `"false"`
- 代码会自动转换为布尔类型

### 6. 数值类型

- `MAX_PRODUCTS_PER_SEARCH`、`DELAY_MIN`、`DELAY_MAX` 等应该使用数字或字符串数字
- 代码会自动转换为相应类型

---

## 🔧 故障排查

### 问题 1：MongoDB 连接失败

**症状：** 日志显示 `MongoServerError` 或连接超时

**解决方案：**
1. 检查 `MONGODB_URL` 是否正确
2. 检查 MongoDB Atlas 网络访问列表是否包含 Railway IP
3. 检查密码是否包含特殊字符，需要 URL 编码
4. 检查 `MONGODB_DATABASE` 是否正确

### 问题 2：前端无法连接后端

**症状：** 前端显示网络错误或 CORS 错误

**解决方案：**
1. 确保 `VITE_API_BASE_URL` 留空（使用相对路径）
2. 检查 `ENV=production` 已设置
3. 检查 Railway 公共域名是否正确
4. 查看浏览器控制台错误信息

### 问题 3：AI 分析功能不可用

**症状：** AI 分析返回错误或功能不可用

**解决方案：**
1. 检查 `GOOGLE_AI_API_KEY` 是否设置
2. 检查 API 密钥是否有效
3. 查看日志中的错误信息
4. 注意：即使没有 API 密钥，应用也能正常运行，只是 AI 功能不可用

### 问题 4：爬虫功能异常

**症状：** 爬虫无法正常工作或返回错误

**解决方案：**
1. 检查 `HEADLESS=true` 设置
2. 检查 `DELAY_MIN` 和 `DELAY_MAX` 是否合理（建议 2-5 秒）
3. 如果使用代理，检查 `PROXY` 配置
4. 查看日志中的详细错误信息

---

## 📚 相关文档

- `RAILWAY_ENV_VARIABLES.md` - 基础环境变量配置
- `verify_backend.sh` - 后端验证脚本
- `app/config.py` - 后端配置定义
- `src/services/ProductService.js` - 前端 API 服务

---

## 🔄 更新日志

- **2025-11-28**: 创建完整环境变量配置文档
- 包含所有后端和前端环境变量
- 添加故障排查指南
- 添加批量配置方法

