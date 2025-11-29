# Cross-Border-E-Commerce-Bestseller-Analyzer

跨境电商爆款分析器 - 前后端分离架构

## 🎯 项目简介

基于 BeautifulSoup 的 Amazon 商品爬取与分析系统，支持：
- 输入关键字爬取商品数据
- 自动存储到 MongoDB
- 查询历史管理（保留最近5次查询）
- 自动清理旧数据
- 前后端分离架构

## 🏗️ 架构

### 后端 (FastAPI)
- REST API 服务
- BeautifulSoup 爬虫
- MongoDB 数据存储
- 查询历史管理

### 前端 (Vue.js)
- 独立前端应用
- 通过 HTTP API 与后端通信
- 产品展示、搜索、对比等功能

## 📋 环境要求

- Python 3.10+
- Node.js 16+
- MongoDB (本地或 Atlas)

## ⚙️ 环境配置

创建 `.env` 文件：

```env
# MongoDB (必需)
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=amazon_products

# Firecrawl (可选，当前未使用)
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# PostgreSQL (可选，保留备用)
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<database>
```

## 📦 安装依赖

### 后端
```bash
pip install -r requirements.txt
```

### 前端
```bash
npm install
```

## 🚀 启动服务

### 后端 API
```bash
python3 run_api.py
```
API 运行在: http://localhost:8000
API 文档: http://localhost:8000/docs

### 前端应用
```bash
npm run dev
```
前端运行在: http://localhost:3001

## 📡 API 端点

### POST /api/scrape/
爬取商品数据
```json
{
  "search_terms": ["men's t-shirt"],
  "fetch_details": false,
  "max_products": 20
}
```

### GET /api/products/
获取产品列表
- 支持分页、搜索、过滤
- 从 MongoDB 读取数据

## 🔄 数据流程

```
用户输入关键字 
  ↓
POST /api/scrape/ (BeautifulSoup 爬取)
  ↓
存储到 MongoDB
  ↓
保存查询历史
  ↓
自动清理（保留最近5次）
  ↓
GET /api/products/ (从 MongoDB 读取)
  ↓
前端展示
```

## 📁 项目结构

```
├── app/                    # 后端代码
│   ├── api/               # API 端点
│   ├── services/          # 业务逻辑
│   ├── scrapers/          # 爬虫（BeautifulSoup）
│   └── db/               # 数据库连接
├── src/                   # 前端代码（Vue.js）
├── scripts/               # 独立工具脚本
└── run_api.py            # API 启动脚本
```

## 🛠️ 独立工具

### 命令行爬取
```bash
python3 scripts/crawl_beautifulsoup.py
```
独立运行爬虫，保存 JSON 并写入 MongoDB。

## 📝 功能特性

- ✅ 关键字搜索爬取
- ✅ MongoDB 数据存储
- ✅ 查询历史管理
- ✅ 自动数据清理（保留最近5次）
- ✅ 前后端完全分离
- ✅ REST API 接口

## 🚀 部署

### Railway 部署
项目已配置 Railway 部署，详细步骤请参考：
- **[RAILWAY_DEPLOY.md](./RAILWAY_DEPLOY.md)** - Railway 部署完整指南
- **[DEPLOY_CHECKLIST.md](./DEPLOY_CHECKLIST.md)** - 部署检查清单

快速开始：
1. 连接 GitHub 仓库到 Railway
2. 配置环境变量（MongoDB 连接等）
3. 部署自动完成

## 📚 文档

- `RAILWAY_DEPLOY.md` - Railway 部署指南
- `DEPLOY_CHECKLIST.md` - 部署检查清单
- `MONGODB_SETUP.md` - MongoDB 配置指南
- `AGENTS.md` - 开发规范

## 🔧 技术栈

- **后端**: FastAPI, BeautifulSoup, MongoDB, Pydantic
- **前端**: Vue.js 3, Pinia, Vue Router, Vite
- **数据库**: MongoDB

## 📄 许可证

MIT
