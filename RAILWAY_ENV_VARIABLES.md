# Railway 环境变量完整配置

## 📋 在 Railway Dashboard 中添加以下环境变量

### 🔴 必需变量（必须设置）

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `MONGODB_URL` | `mongodb+srv://Ziyinzx_db_user:qihTWbIOb3HHvj22@cluster0.y0kykwv.mongodb.net/?retryWrites=true&w=majority` | MongoDB 连接字符串 |
| `MONGODB_DATABASE` | `amazon_products` | 数据库名称 |
| `ENV` | `production` | 环境类型（必须为 production） |
| `VITE_API_BASE_URL` | (留空) | 前端 API 基础 URL（留空使用相对路径） |

### 🟡 推荐变量（建议设置）

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `LOG_LEVEL` | `INFO` | 日志级别（DEBUG/INFO/WARNING/ERROR） |

### 🟢 可选变量（根据需要设置）

#### AI 分析功能
| 变量名 | 值 | 说明 |
|--------|-----|------|
| `GOOGLE_AI_API_KEY` | (你的 Google AI API Key) | Google Gemini API 密钥（用于 AI 分析功能） |

#### 爬虫设置
| 变量名 | 值 | 说明 |
|--------|-----|------|
| `MAX_PRODUCTS_PER_SEARCH` | `20` | 每次搜索最大产品数 |
| `DELAY_MIN` | `2.0` | 爬虫延迟最小值（秒） |
| `DELAY_MAX` | `5.0` | 爬虫延迟最大值（秒） |
| `HEADLESS` | `true` | 无头浏览器模式（true/false） |
| `ENABLE_REQUEST_MONITORING` | `true` | 启用请求监控（true/false） |

#### 代理设置（如果需要）
| 变量名 | 值 | 说明 |
|--------|-----|------|
| `PROXY` | (留空) | 代理服务器地址（格式: http://user:pass@host:port） |

#### 其他设置（通常不需要修改）
| 变量名 | 值 | 说明 |
|--------|-----|------|
| `OUTPUT_DIR` | `data/scraped_content` | 爬取内容输出目录 |
| `LOG_FILE` | `data/logs/scraper.log` | 日志文件路径 |
| `COOKIES_FILE` | `data/cookies.json` | Cookies 文件路径 |

### 🔵 Railway 自动设置（无需手动添加）

以下变量由 Railway 自动设置，无需手动配置：

- `PORT` - Railway 自动提供端口号
- `RAILWAY_PUBLIC_DOMAIN` - Railway 自动提供公共域名（部署后）

---

## 📝 快速复制配置

### 最小配置（必需变量）

在 Railway Dashboard → Variables 中添加：

```
MONGODB_URL=mongodb+srv://Ziyinzx_db_user:qihTWbIOb3HHvj22@cluster0.y0kykwv.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=amazon_products
ENV=production
VITE_API_BASE_URL=
```

### 完整配置（推荐）

```
MONGODB_URL=mongodb+srv://Ziyinzx_db_user:qihTWbIOb3HHvj22@cluster0.y0kykwv.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=amazon_products
ENV=production
VITE_API_BASE_URL=
LOG_LEVEL=INFO
MAX_PRODUCTS_PER_SEARCH=20
DELAY_MIN=2.0
DELAY_MAX=5.0
HEADLESS=true
ENABLE_REQUEST_MONITORING=true
```

### 包含 AI 功能的配置

```
MONGODB_URL=mongodb+srv://Ziyinzx_db_user:qihTWbIOb3HHvj22@cluster0.y0kykwv.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=amazon_products
ENV=production
VITE_API_BASE_URL=
LOG_LEVEL=INFO
GOOGLE_AI_API_KEY=你的_google_ai_api_key
MAX_PRODUCTS_PER_SEARCH=20
DELAY_MIN=2.0
DELAY_MAX=5.0
HEADLESS=true
ENABLE_REQUEST_MONITORING=true
```

---

## 🚀 在 Railway 中设置步骤

1. 登录 Railway Dashboard: https://railway.app
2. 选择你的项目
3. 点击项目名称进入项目设置
4. 点击 **"Variables"** 标签
5. 点击 **"New Variable"** 添加每个变量
6. 输入变量名和值
7. 点击 **"Add"** 保存

**提示：** 可以一次性添加多个变量，每个变量一行。

---

## ✅ 验证配置

部署后，可以通过以下方式验证：

1. **检查环境变量是否加载**
   ```bash
   # 在 Railway 日志中查看
   # 或通过 API 端点检查（如果添加了调试端点）
   ```

2. **测试 MongoDB 连接**
   - 访问应用
   - 尝试爬取产品
   - 检查数据是否保存到 MongoDB

3. **检查日志**
   - Railway Dashboard → Deployments → View Logs
   - 查看是否有配置相关的错误

---

## ⚠️ 注意事项

1. **MONGODB_URL** 中的密码如果包含特殊字符，需要进行 URL 编码
2. **VITE_API_BASE_URL** 必须留空，使用相对路径
3. **ENV** 必须设置为 `production`，否则静态文件服务不会启用
4. **GOOGLE_AI_API_KEY** 是可选的，只有使用 AI 分析功能时才需要
5. Railway 会自动设置 `PORT` 和 `RAILWAY_PUBLIC_DOMAIN`，无需手动配置

---

## 🔗 相关文档

- `RAILWAY_DEPLOY.md` - 完整部署指南
- `RAILWAY_DEPLOY_CHECK.md` - 部署检查报告
- `DEPLOY_CHECKLIST.md` - 部署检查清单

