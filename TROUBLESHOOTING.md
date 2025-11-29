# 问题排查指南 - 一步步拆解

## 🔍 问题现象
前端仍然尝试访问 `http://localhost:8000`，导致 CORS 错误

## 📋 排查步骤

### 步骤 1: 检查浏览器控制台日志

1. 打开浏览器访问：`https://e-commerce-analyzer-production.up.railway.app/search`
2. 按 F12 打开开发者工具
3. 查看 Console 标签页

**需要检查的内容：**
- 查找 `[ProductService] Environment:` 日志
- 查看 `API_BASE_URL` 的值
- 查看 `hostname` 的值
- 查看是否有 CORS 错误

**预期结果：**
```javascript
[ProductService] Environment: {
  MODE: "production",
  PROD: true,
  VITE_API_BASE_URL: undefined,
  API_BASE_URL: "",  // 应该是空字符串
  hostname: "e-commerce-analyzer-production.up.railway.app",
  origin: "https://e-commerce-analyzer-production.up.railway.app"
}
```

### 步骤 2: 检查构建产物

**问题可能在这里！** 如果构建时 `getApiBaseUrl()` 函数被优化，可能仍然使用旧的值。

**检查方法：**
1. 在浏览器中打开：`https://e-commerce-analyzer-production.up.railway.app/assets/index-*.js`
2. 搜索 `localhost:8000`
3. 如果找到，说明构建产物仍然包含硬编码的 localhost

### 步骤 3: 检查网络请求

1. 打开 Network 标签页
2. 刷新页面
3. 查找对 `/api/products/` 的请求

**检查内容：**
- 请求 URL 是什么？
- 如果是 `http://localhost:8000/api/products/` → 问题确认
- 如果是 `/api/products/` 或 `https://e-commerce-analyzer-production.up.railway.app/api/products/` → 正常

### 步骤 4: 检查环境变量

在 Railway Dashboard 中检查：
1. Variables 标签页
2. 确认 `VITE_API_BASE_URL` 是否设置（应该留空或未设置）

### 步骤 5: 检查构建日志

在 Railway Dashboard → Deployments → Build Logs 中检查：
1. `npm run build` 是否成功
2. 是否有任何警告或错误
3. 构建时 `NODE_ENV` 是否为 `production`

## 🛠️ 可能的解决方案

### 方案 A: 强制重新构建

如果构建产物有问题，需要强制重新构建：

1. 在 Railway Dashboard 中删除 `dist` 目录（如果存在）
2. 触发新的部署
3. 确保构建时 `NODE_ENV=production`

### 方案 B: 使用环境变量

如果运行时检查不工作，可以明确设置环境变量：

在 Railway Variables 中设置：
```
VITE_API_BASE_URL=
```

注意：留空表示使用相对路径

### 方案 C: 修改代码逻辑

如果 `getApiBaseUrl()` 函数在构建时被优化，可以改为更简单的方式：

```javascript
// 完全依赖运行时检查，不依赖构建时变量
const API_BASE_URL = (() => {
  if (typeof window === 'undefined') return ''
  const hostname = window.location.hostname
  return (hostname === 'localhost' || hostname === '127.0.0.1') 
    ? 'http://localhost:8000' 
    : ''
})()
```

## 📊 当前排查结果

根据刚才的检查：
- ✅ 后端服务正常
- ✅ API 端点正常
- ✅ CORS 配置正常
- ✅ 静态文件服务正常
- ⚠️  需要检查前端构建产物

## 🎯 下一步行动

1. **立即检查**：在浏览器控制台查看 `[ProductService] Environment` 日志
2. **如果 API_BASE_URL 仍然是 localhost:8000**：
   - 检查构建产物
   - 可能需要强制重新构建
3. **如果 API_BASE_URL 是空字符串但仍然有 CORS 错误**：
   - 检查 CORS 配置
   - 检查请求头

