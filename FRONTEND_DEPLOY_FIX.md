# 前端部署问题修复

## 问题
访问 https://e-commerce-analyzer-production.up.railway.app/ 只返回 JSON，而不是前端页面。

## 原因分析

1. **环境变量未设置**：`ENV=production` 可能没有在 Railway 中设置
2. **dist 目录不存在**：前端可能没有正确构建
3. **路径问题**：静态文件路径可能不正确

## 解决方案

### 1. 检查 Railway 环境变量

在 Railway Dashboard → Variables 中确保设置了：
```
ENV=production
```

### 2. 检查构建日志

查看 Railway 构建日志，确认：
- `npm run build` 是否成功执行
- `dist/` 目录是否被创建
- `dist/index.html` 文件是否存在

### 3. 验证部署

部署后，检查日志中的调试信息：
```
[DEBUG] is_production: True/False
[DEBUG] dist_path: /app/dist
[DEBUG] exists: True/False
```

## 修复内容

已更新代码：
1. 改进了生产环境检测（即使 ENV 未设置，如果 PORT 存在也认为是生产环境）
2. 添加了调试日志
3. 改进了错误处理

## 验证步骤

1. **检查环境变量**
   ```bash
   # 在 Railway Dashboard → Variables 中查看
   ENV=production  # 必须设置
   ```

2. **查看部署日志**
   - Railway Dashboard → Logs
   - 查找 `[DEBUG]` 开头的日志
   - 确认 `is_production: True` 和 `dist_exists: True`

3. **测试访问**
   - 访问根路径：`https://your-app.railway.app/`
   - 应该看到前端页面，而不是 JSON

4. **如果还是不行**
   - 检查构建日志，确认 `npm run build` 成功
   - 检查 `dist/` 目录是否在 `.railwayignore` 中被忽略（不应该忽略）
   - 查看 Railway Logs 中的错误信息

## 临时调试

如果问题仍然存在，可以在 Railway Logs 中查看：
- `is_production` 的值
- `dist_path` 的路径
- `dist_exists` 的值

这些信息会帮助定位问题。

