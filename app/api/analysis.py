"""
数据分析 API 端点
提供各种数据分析功能：价格趋势、分类分析、数据质量等
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import re

from app.db.mongodb import mongodb
from app.services.mongodb_reader import ProductResponse
from app.services.ai_analysis import analyze_with_ai

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def parse_review_count(review_count_text: Optional[str]) -> Optional[int]:
    """从 review_count_text 解析评论数"""
    if not review_count_text:
        return None
    
    # 移除逗号和其他字符，只保留数字
    numbers = re.findall(r'\d+', review_count_text.replace(',', ''))
    if numbers:
        try:
            return int(numbers[0])
        except:
            pass
    return None


@router.get("/price-trend")
async def get_price_trend(
    days: int = Query(30, description="分析最近 N 天的价格趋势"),
    category: Optional[str] = Query(None, description="分类筛选"),
    platform: Optional[str] = Query(None, description="平台筛选")
) -> Dict[str, Any]:
    """获取价格趋势分析"""
    db = mongodb.connect()
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB not configured")
    
    try:
        products_collection = db["products"]
        
        # 构建查询条件
        query = {}
        if category:
            query["categories"] = {"$in": [category]}
        if platform:
            query["platform"] = platform
        
        # 获取时间范围
        start_date = datetime.utcnow() - timedelta(days=days)
        query["created_at"] = {"$gte": start_date}
        
        # 获取产品数据
        products = list(products_collection.find(query))
        
        # 解析价格
        price_data = []
        for product in products:
            price_str = product.get("price", "")
            if isinstance(price_str, str):
                # 移除 $ 和逗号
                price_clean = re.sub(r'[$,]', '', price_str)
                try:
                    price = float(price_clean)
                    price_data.append({
                        "price": price,
                        "date": product.get("created_at"),
                        "product_id": str(product.get("_id", "")),
                        "name": product.get("name", "")
                    })
                except:
                    pass
        
        if not price_data:
            return {
                "period": days,
                "average_price": 0,
                "min_price": 0,
                "max_price": 0,
                "price_distribution": [],
                "trend": "stable"
            }
        
        prices = [d["price"] for d in price_data]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        # 价格分布（按区间）
        price_ranges = {
            "0-20": 0,
            "20-50": 0,
            "50-100": 0,
            "100-200": 0,
            "200+": 0
        }
        for price in prices:
            if price < 20:
                price_ranges["0-20"] += 1
            elif price < 50:
                price_ranges["20-50"] += 1
            elif price < 100:
                price_ranges["50-100"] += 1
            elif price < 200:
                price_ranges["100-200"] += 1
            else:
                price_ranges["200+"] += 1
        
        # 趋势分析（简单：比较前半段和后半段）
        sorted_data = sorted(price_data, key=lambda x: x["date"] if x["date"] else datetime.min)
        mid_point = len(sorted_data) // 2
        first_half_avg = sum([d["price"] for d in sorted_data[:mid_point]]) / max(mid_point, 1)
        second_half_avg = sum([d["price"] for d in sorted_data[mid_point:]]) / max(len(sorted_data) - mid_point, 1)
        
        if second_half_avg > first_half_avg * 1.05:
            trend = "increasing"
        elif second_half_avg < first_half_avg * 0.95:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "period": days,
            "average_price": round(avg_price, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "price_distribution": [
                {"range": k, "count": v} for k, v in price_ranges.items()
            ],
            "trend": trend,
            "trend_percentage": round(((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze price trend: {str(e)}")
    finally:
        mongodb.close()


@router.get("/category-distribution")
async def get_category_distribution(
    platform: Optional[str] = Query(None, description="平台筛选")
) -> Dict[str, Any]:
    """获取分类分布分析"""
    db = mongodb.connect()
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB not configured")
    
    try:
        products_collection = db["products"]
        
        query = {}
        if platform:
            query["platform"] = platform
        
        # 聚合统计分类
        pipeline = [
            {"$match": query},
            {"$unwind": "$categories"},
            {"$group": {
                "_id": "$categories",
                "count": {"$sum": 1},
                "avg_price": {"$avg": {"$toDouble": {"$replaceAll": {"input": {"$toString": "$price"}, "find": "$", "replacement": ""}}}},
                "avg_rating": {"$avg": "$rating"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        results = list(products_collection.aggregate(pipeline))
        
        categories = []
        for result in results:
            category_name = result.get("_id", "Unknown")
            # 处理价格
            avg_price = result.get("avg_price", 0)
            if avg_price is None:
                avg_price = 0
            
            categories.append({
                "name": category_name,
                "count": result.get("count", 0),
                "average_price": round(avg_price, 2),
                "average_rating": round(result.get("avg_rating", 0), 2) if result.get("avg_rating") else None
            })
        
        total_products = sum(c["count"] for c in categories)
        
        return {
            "total_products": total_products,
            "total_categories": len(categories),
            "categories": categories,
            "platform": platform or "all"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze category distribution: {str(e)}")
    finally:
        mongodb.close()


@router.get("/data-quality")
async def get_data_quality() -> Dict[str, Any]:
    """获取数据质量分析"""
    db = mongodb.connect()
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB not configured")
    
    try:
        products_collection = db["products"]
        total_products = products_collection.count_documents({})
        
        if total_products == 0:
            return {
                "total_products": 0,
                "quality_score": 0,
                "issues": []
            }
        
        # 检查各种数据质量问题
        issues = []
        
        # 检查缺失字段
        missing_price = products_collection.count_documents({"price": {"$in": [None, ""]}})
        missing_name = products_collection.count_documents({"name": {"$in": [None, ""]}})
        missing_image = products_collection.count_documents({"image_url": {"$in": [None, ""]}})
        missing_url = products_collection.count_documents({"product_url": {"$in": [None, ""]}})
        missing_rating = products_collection.count_documents({"rating": None})
        missing_review_count = products_collection.count_documents({"review_count": None, "review_count_text": {"$in": [None, ""]}})
        
        if missing_price > 0:
            issues.append({
                "type": "missing_price",
                "count": missing_price,
                "percentage": round(missing_price / total_products * 100, 2),
                "severity": "high"
            })
        
        if missing_name > 0:
            issues.append({
                "type": "missing_name",
                "count": missing_name,
                "percentage": round(missing_name / total_products * 100, 2),
                "severity": "critical"
            })
        
        if missing_image > 0:
            issues.append({
                "type": "missing_image",
                "count": missing_image,
                "percentage": round(missing_image / total_products * 100, 2),
                "severity": "medium"
            })
        
        if missing_url > 0:
            issues.append({
                "type": "missing_url",
                "count": missing_url,
                "percentage": round(missing_url / total_products * 100, 2),
                "severity": "medium"
            })
        
        if missing_rating > 0:
            issues.append({
                "type": "missing_rating",
                "count": missing_rating,
                "percentage": round(missing_rating / total_products * 100, 2),
                "severity": "low"
            })
        
        if missing_review_count > 0:
            issues.append({
                "type": "missing_review_count",
                "count": missing_review_count,
                "percentage": round(missing_review_count / total_products * 100, 2),
                "severity": "low"
            })
        
        # 计算质量分数（100分制，每个问题扣分）
        quality_score = 100
        for issue in issues:
            if issue["severity"] == "critical":
                quality_score -= issue["percentage"] * 2
            elif issue["severity"] == "high":
                quality_score -= issue["percentage"] * 1.5
            elif issue["severity"] == "medium":
                quality_score -= issue["percentage"] * 1
            else:
                quality_score -= issue["percentage"] * 0.5
        
        quality_score = max(0, min(100, quality_score))
        
        return {
            "total_products": total_products,
            "quality_score": round(quality_score, 2),
            "issues": issues,
            "completeness": round((total_products - len([i for i in issues if i["count"] > 0])) / total_products * 100, 2) if total_products > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze data quality: {str(e)}")
    finally:
        mongodb.close()


@router.get("/competition-analysis")
async def get_competition_analysis(
    category: Optional[str] = Query(None, description="分类筛选"),
    platform: Optional[str] = Query(None, description="平台筛选")
) -> Dict[str, Any]:
    """获取竞争度分析"""
    db = mongodb.connect()
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB not configured")
    
    try:
        products_collection = db["products"]
        
        query = {}
        if category:
            query["categories"] = {"$in": [category]}
        if platform:
            query["platform"] = platform
        
        products = list(products_collection.find(query))
        
        # 计算竞争度分数
        competition_scores = []
        for product in products:
            review_count = product.get("review_count")
            if review_count is None:
                review_count = parse_review_count(product.get("review_count_text"))
            
            rating = product.get("rating", 0) or 0
            
            # 竞争度计算：基于评论数和评分
            if review_count and rating:
                # 评论数权重 0.6，评分权重 0.4
                score = (min(review_count / 1000, 1) * 60) + (rating / 5 * 40)
                competition_scores.append({
                    "score": score,
                    "level": "high" if score > 60 else ("medium" if score > 30 else "low"),
                    "product_id": str(product.get("_id", "")),
                    "name": product.get("name", "")
                })
        
        if not competition_scores:
            return {
                "total_products": 0,
                "average_competition_score": 0,
                "competition_distribution": {"low": 0, "medium": 0, "high": 0},
                "blue_ocean_products": []
            }
        
        avg_score = sum(c["score"] for c in competition_scores) / len(competition_scores)
        
        # 竞争度分布
        distribution = {"low": 0, "medium": 0, "high": 0}
        for c in competition_scores:
            distribution[c["level"]] += 1
        
        # 蓝海产品（低竞争度）
        blue_ocean = [c for c in competition_scores if c["level"] == "low"][:10]
        
        return {
            "total_products": len(competition_scores),
            "average_competition_score": round(avg_score, 2),
            "competition_distribution": distribution,
            "blue_ocean_products": blue_ocean,
            "category": category or "all",
            "platform": platform or "all"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze competition: {str(e)}")
    finally:
        mongodb.close()


@router.get("/batch-analysis")
async def get_batch_analysis(
    limit: int = Query(10, description="分析最近 N 个批次")
) -> Dict[str, Any]:
    """获取爬取批次分析"""
    db = mongodb.connect()
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB not configured")
    
    try:
        products_collection = db["products"]
        
        # 按 run_id 分组统计
        pipeline = [
            {"$group": {
                "_id": "$run_id",
                "count": {"$sum": 1},
                "first_created": {"$min": "$created_at"},
                "last_updated": {"$max": "$updated_at"}
            }},
            {"$sort": {"first_created": -1}},
            {"$limit": limit}
        ]
        
        batches = list(products_collection.aggregate(pipeline))
        
        batch_details = []
        for batch in batches:
            run_id = batch.get("_id", "unknown")
            if not run_id:
                continue
            
            # 获取该批次的产品详情
            batch_products = list(products_collection.find({"run_id": run_id}).limit(5))
            
            batch_details.append({
                "run_id": run_id,
                "product_count": batch.get("count", 0),
                "first_created": batch.get("first_created").isoformat() if batch.get("first_created") else None,
                "last_updated": batch.get("last_updated").isoformat() if batch.get("last_updated") else None,
                "sample_products": [p.get("name", "")[:50] for p in batch_products]
            })
        
        return {
            "total_batches": len(batch_details),
            "batches": batch_details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze batches: {str(e)}")
    finally:
        mongodb.close()


@router.get("/platform-comparison")
async def get_platform_comparison() -> Dict[str, Any]:
    """获取平台对比分析"""
    db = mongodb.connect()
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB not configured")
    
    try:
        products_collection = db["products"]
        
        # 按平台聚合
        pipeline = [
            {"$group": {
                "_id": "$platform",
                "count": {"$sum": 1},
                "avg_price": {"$avg": {"$toDouble": {"$replaceAll": {"input": {"$toString": "$price"}, "find": "$", "replacement": ""}}}},
                "avg_rating": {"$avg": "$rating"},
                "total_reviews": {"$sum": {"$ifNull": ["$review_count", 0]}}
            }},
            {"$sort": {"count": -1}}
        ]
        
        platforms = list(products_collection.aggregate(pipeline))
        
        platform_data = []
        for platform in platforms:
            platform_name = platform.get("_id", "unknown")
            avg_price = platform.get("avg_price", 0)
            if avg_price is None:
                avg_price = 0
            
            platform_data.append({
                "platform": platform_name,
                "product_count": platform.get("count", 0),
                "average_price": round(avg_price, 2),
                "average_rating": round(platform.get("avg_rating", 0), 2) if platform.get("avg_rating") else None,
                "total_reviews": platform.get("total_reviews", 0)
            })
        
        return {
            "platforms": platform_data,
            "total_platforms": len(platform_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare platforms: {str(e)}")
    finally:
        mongodb.close()


@router.get("/ai-insights")
async def get_ai_insights(
    limit: int = Query(50, description="分析的产品数量限制", ge=1, le=200),
    category: Optional[str] = Query(None, description="分类筛选"),
    platform: Optional[str] = Query(None, description="平台筛选")
) -> Dict[str, Any]:
    """获取 AI 分析洞察"""
    try:
        result = await analyze_with_ai(limit=limit, category=category, platform=platform)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get AI insights: {str(e)}")

