# 数据映射文档

## 后端 → 前端字段映射

### 核心字段（必需）
| 后端字段 | 前端字段 | 说明 | 计算/来源 |
|---------|---------|------|----------|
| `name` | `title` / `name` | 产品名称 | 爬取数据 |
| `price` | `price` | 价格（数字） | 爬取数据，解析后为 float |
| `price` (字符串) | `formattedPrice` | 格式化价格 | 原始价格字符串或 `$${price:.2f}` |
| 计算值 | `marginRate` | 利润率（%） | `_calculate_margin_rate(price)` |
| 计算值 | `competitionScore` | 竞争分数（0-100） | `_calculate_competition_score(review_count, rating)` |
| 计算值 | `competitionLevel` | 竞争等级 | `_get_competition_level(competition_score)` → "low"/"medium"/"high" |
| `categories[0].name` | `category` | 分类 | 从分类列表取第一个 |
| `image_url` | `imageUrl` | 图片URL | 爬取数据 |
| `description` | `description` | 描述 | 爬取数据 |
| `rating` | `rating` | 评分 | 爬取数据 |
| `review_count` | `reviewCount` | 评论数 | 爬取数据 |
| `product_url` | `productUrl` | 产品链接 | 爬取数据 |
| `platform` | `platform` | 平台 | 默认为 "amazon" |
| `content_hash[:12]` | `id` | 产品ID | `prod-{content_hash[:12]}` |

### 分析字段计算逻辑

#### 利润率 (marginRate)
```python
cost = price * 0.6  # 成本为价格的60%
margin = ((price - cost) / cost) * 100
```
- 示例：价格 $50 → 成本 $30 → 利润率 66.67%

#### 竞争分数 (competitionScore)
```python
score = 50.0  # 基础分数
if review_count > 10000: score += 30
elif review_count > 5000: score += 20
elif review_count > 1000: score += 10
if rating >= 4.5: score += 20
elif rating >= 4.0: score += 10
score = min(100.0, max(0.0, score))
```

#### 竞争等级 (competitionLevel)
- `score < 30` → `"low"` (低竞争，蓝海)
- `30 <= score < 60` → `"medium"` (中等竞争)
- `score >= 60` → `"high"` (高竞争，红海)

### 前端分析功能对应

#### 1. 利润率分析
- **字段**: `marginRate`
- **显示**: ProductCard 中的利润率百分比
- **标签**: 
  - `marginRate > 30%` → "爆款潜质" 🔥
  - `marginRate >= 15%` → "潜力不错"
- **样式**: 
  - `margin-high` (红色) - > 30%
  - `margin-medium` (绿色) - 15-30%
  - `margin-low` (灰色) - < 15%

#### 2. 竞争度分析
- **字段**: `competitionScore`, `competitionLevel`
- **显示**: ProductCard 中的竞争程度
- **标签**:
  - `low` → "蓝海"
  - `medium` → "竞争激烈"
  - `high` → "红海"
- **样式**:
  - `competition-low` (绿色)
  - `competition-medium` (黄色)
  - `competition-high` (红色)

#### 3. 价格分析
- **字段**: `price`, `formattedPrice`
- **功能**: 价格筛选、排序
- **显示**: 格式化后的价格字符串

#### 4. 销量估算
- **字段**: `reviewCount` (作为 `sales` 的近似值)
- **功能**: 销量排序
- **计算**: `sales = reviewCount || 0`

#### 5. 评分分析
- **字段**: `rating`
- **功能**: 评分排序、筛选
- **显示**: 星级评分

#### 6. 分类筛选
- **字段**: `category`
- **功能**: 按分类筛选产品
- **来源**: `categories[0].name`

#### 7. 平台筛选
- **字段**: `platform`
- **功能**: 按平台筛选产品
- **默认**: "amazon"

### 数据流

```
爬取 (BeautifulSoup)
  ↓
转换为 ProductWithCategories
  ↓
存储到 MongoDB
  ↓
读取 (mongodb_reader.py)
  ↓
转换为 ProductResponse (计算 marginRate, competitionScore, competitionLevel)
  ↓
API 返回 (JSON)
  ↓
前端 ProductService._normalizeApiProduct()
  ↓
前端 ProductStore
  ↓
组件显示 (ProductCard, Search.vue 等)
```

### 验证清单

- [x] 利润率计算逻辑统一
- [x] 竞争度计算逻辑统一
- [x] 竞争等级阈值统一（30/60）
- [x] 所有必需字段都有映射
- [x] 前端组件能正确读取所有字段
- [x] 分析功能能正确使用计算字段
