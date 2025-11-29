"""
AI 分析服务
使用 Google Gemini API 分析爬取的产品数据，提供深度洞察
"""

import google.generativeai as genai
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.db.mongodb import mongodb
import json
import re


def _parse_price(price_str: Optional[str]) -> float:
    """解析价格字符串为数字"""
    if not price_str:
        return 0.0
    cleaned = re.sub(r'[$,]', '', str(price_str))
    try:
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0


def _parse_review_count(review_count_text: Optional[str]) -> Optional[int]:
    """从 review_count_text 解析评论数"""
    if not review_count_text:
        return None
    numbers = re.findall(r'\d+', review_count_text.replace(',', ''))
    if numbers:
        try:
            return int(numbers[0])
        except:
            pass
    return None


def _prepare_product_summary(products: List[Dict]) -> str:
    """准备产品数据摘要，用于 AI 分析"""
    if not products:
        return "No products available for analysis."
    
    summary_parts = []
    summary_parts.append(f"Total products: {len(products)}\n")
    
    # 价格统计
    prices = []
    ratings = []
    review_counts = []
    categories = []
    
    for product in products:
        price_str = product.get("price", "")
        if price_str:
            price = _parse_price(price_str)
            if price > 0:
                prices.append(price)
        
        rating = product.get("rating")
        if rating:
            ratings.append(float(rating))
        
        review_count = product.get("review_count")
        if review_count is None:
            review_count = _parse_review_count(product.get("review_count_text"))
        if review_count:
            review_counts.append(review_count)
        
        product_categories = product.get("categories", [])
        if isinstance(product_categories, list):
            categories.extend(product_categories)
        elif product_categories:
            categories.append(str(product_categories))
    
    # 价格分析
    if prices:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        summary_parts.append(f"\nPrice Analysis:")
        summary_parts.append(f"  - Average: ${avg_price:.2f}")
        summary_parts.append(f"  - Range: ${min_price:.2f} - ${max_price:.2f}")
        summary_parts.append(f"  - Products with price: {len(prices)}/{len(products)}")
    
    # 评分分析
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        summary_parts.append(f"\nRating Analysis:")
        summary_parts.append(f"  - Average rating: {avg_rating:.2f}/5.0")
        summary_parts.append(f"  - Products with rating: {len(ratings)}/{len(products)}")
    
    # 评论数分析
    if review_counts:
        avg_reviews = sum(review_counts) / len(review_counts)
        max_reviews = max(review_counts)
        summary_parts.append(f"\nReview Count Analysis:")
        summary_parts.append(f"  - Average reviews: {avg_reviews:.0f}")
        summary_parts.append(f"  - Max reviews: {max_reviews:,}")
        summary_parts.append(f"  - Products with reviews: {len(review_counts)}/{len(products)}")
    
    # 分类分析
    if categories:
        from collections import Counter
        category_counts = Counter(categories)
        top_categories = category_counts.most_common(5)
        summary_parts.append(f"\nCategory Analysis:")
        summary_parts.append(f"  - Total categories: {len(category_counts)}")
        summary_parts.append(f"  - Top categories:")
        for cat, count in top_categories:
            summary_parts.append(f"    • {cat}: {count} products")
    
    # 平台分析
    platforms = {}
    for product in products:
        platform = product.get("platform", "unknown")
        platforms[platform] = platforms.get(platform, 0) + 1
    
    if platforms:
        summary_parts.append(f"\nPlatform Analysis:")
        for platform, count in platforms.items():
            summary_parts.append(f"  - {platform}: {count} products")
    
    # 样本产品名称
    sample_names = [p.get("name", "")[:50] for p in products[:10]]
    if sample_names:
        summary_parts.append(f"\nSample Product Names:")
        for i, name in enumerate(sample_names, 1):
            summary_parts.append(f"  {i}. {name}")
    
    return "\n".join(summary_parts)


async def analyze_with_ai(
    limit: int = 50,
    category: Optional[str] = None,
    platform: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用 Google Gemini AI 分析产品数据
    
    Args:
        limit: 分析的产品数量限制
        category: 分类筛选
        platform: 平台筛选
    
    Returns:
        包含 AI 分析结果的字典
    """
    # 检查 API key
    if not settings.google_ai_api_key:
        return {
            "error": "Google AI API key not configured",
            "insights": None
        }
    
    # 配置 Gemini
    try:
        genai.configure(api_key=settings.google_ai_api_key)
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        return {
            "error": f"Failed to configure AI model: {str(e)}",
            "insights": None
        }
    
    # 从 MongoDB 获取产品数据
    db = mongodb.connect()
    if db is None:
        return {
            "error": "MongoDB not configured",
            "insights": None
        }
    
    try:
        products_collection = db["products"]
        
        # 构建查询
        query = {}
        if category:
            query["categories"] = {"$in": [category]}
        if platform:
            query["platform"] = platform
        
        # 获取产品数据
        products = list(products_collection.find(query).limit(limit))
        
        if not products:
            return {
                "error": "No products found for analysis",
                "insights": None,
                "product_count": 0
            }
        
        # 准备数据摘要
        data_summary = _prepare_product_summary(products)
        
        # 构建 AI 提示
        prompt = f"""You are an expert e-commerce data analyst specializing in cross-border e-commerce and Amazon product analysis.

Analyze the following product data and provide actionable business insights:

{data_summary}

Please provide a comprehensive analysis in the following format (respond in English):

1. **Market Opportunities**: Identify potential market opportunities, blue ocean products, or underserved niches based on the data.

2. **Competitive Landscape**: Analyze the competition level, identify high-competition vs low-competition areas, and suggest strategies.

3. **Pricing Insights**: Provide pricing strategy recommendations, identify optimal price points, and highlight pricing opportunities.

4. **Product Quality Indicators**: Analyze product ratings and reviews to identify quality trends and customer satisfaction patterns.

5. **Category Trends**: Identify trending categories, emerging niches, and category-specific opportunities.

6. **Risk Factors**: Highlight potential risks, red flags, or concerns in the data.

7. **Actionable Recommendations**: Provide 3-5 specific, actionable recommendations for sellers or businesses based on this data.

Format your response as a clear, structured analysis with bullet points and specific insights. Be concise but comprehensive."""

        # 调用 AI API
        try:
            response = model.generate_content(prompt)
            ai_insights = response.text
        except Exception as e:
            return {
                "error": f"AI API call failed: {str(e)}",
                "insights": None,
                "product_count": len(products)
            }
        
        return {
            "error": None,
            "insights": ai_insights,
            "product_count": len(products),
            "data_summary": data_summary,
            "analysis_date": str(datetime.utcnow().isoformat())
        }
        
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "insights": None
        }
    finally:
        mongodb.close()

