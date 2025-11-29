"""
MongoDB 数据读取服务
从 MongoDB 读取产品数据，供前端 API 使用
"""

from app.db.mongodb import mongodb
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


def _parse_price(price_str: Optional[str]) -> float:
    """解析價格字符串為數字"""
    if not price_str:
        return 0.0
    import re
    cleaned = re.sub(r'[$,]', '', str(price_str))
    try:
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0


def _calculate_margin_rate(price: float) -> float:
    """計算利潤率"""
    if price <= 0:
        return 0.0
    cost = price * 0.6
    margin = ((price - cost) / cost) * 100
    return round(margin, 2)


def _calculate_competition_score(review_count: Optional[int], rating: Optional[float]) -> float:
    """計算競爭度分數"""
    score = 50.0
    
    if review_count:
        if review_count > 10000:
            score += 30
        elif review_count > 5000:
            score += 20
        elif review_count > 1000:
            score += 10
    
    if rating:
        if rating >= 4.5:
            score += 20
        elif rating >= 4.0:
            score += 10
    
    return min(100.0, max(0.0, score))


def _get_competition_level(score: float) -> str:
    """根據競爭度分數返回等級（與前端 Product 類保持一致：<30=low, 30-60=medium, >=60=high）"""
    if score < 30:
        return "low"
    elif score < 60:  # 與前端 Product.competitionLevel getter 保持一致
        return "medium"
    else:
        return "high"


# 定义 ProductResponse 以避免循环导入
class ProductResponse(BaseModel):
    """產品響應模型（適配前端格式）"""
    id: str
    title: str
    platform: str
    price: float
    formattedPrice: str
    marginRate: float
    competitionScore: float
    competitionLevel: str
    category: str
    imageUrl: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    reviewCount: Optional[int] = None
    productUrl: Optional[str] = None
    tags: List[str] = []
    productDetails: Optional[Dict[str, Any]] = None
    aboutThisItem: Optional[List[str]] = None
    colorOptions: Optional[List[Dict[str, Any]]] = None
    sizeOptions: Optional[List[str]] = None
    
    class Config:
        from_attributes = True


def _parse_review_count(review_count_text: Optional[str]) -> Optional[int]:
    """从 review_count_text 解析评论数"""
    if not review_count_text:
        return None
    
    import re
    # 移除逗号和其他字符，只保留数字
    numbers = re.findall(r'\d+', str(review_count_text).replace(',', ''))
    if numbers:
        try:
            return int(numbers[0])
        except:
            pass
    return None


def _mongo_product_to_response(product_doc: Dict) -> ProductResponse:
    """將 MongoDB 產品文檔轉換為 ProductResponse"""
    try:
        price = _parse_price(product_doc.get("price"))
        margin_rate = _calculate_margin_rate(price)
        
        # 优先使用 review_count，如果为 None 则从 review_count_text 解析
        review_count = product_doc.get("review_count")
        if review_count is None:
            review_count = _parse_review_count(product_doc.get("review_count_text"))
        
        competition_score = _calculate_competition_score(
            review_count,
            product_doc.get("rating")
        )
        competition_level = _get_competition_level(competition_score)
        
        # 獲取分類
        categories = product_doc.get("categories", [])
        category = categories[0] if categories else "General"
        
        # 生成 ID（使用 MongoDB _id 或 content_hash）
        product_id = str(product_doc.get("_id", ""))
        if product_doc.get("content_hash"):
            product_id = f"prod-{product_doc['content_hash'][:12]}"
        else:
            product_id = f"prod-{product_id}"
        
        return ProductResponse(
            id=product_id,
            title=product_doc.get("name", ""),
            platform=product_doc.get("platform", "amazon"),
            price=price,
            formattedPrice=product_doc.get("price") or f"${price:.2f}",
            marginRate=margin_rate,
            competitionScore=competition_score,
            competitionLevel=competition_level,
            category=category,
            imageUrl=product_doc.get("image_url"),
            description=product_doc.get("description"),
            rating=product_doc.get("rating"),
            reviewCount=review_count,  # 使用解析后的评论数
            productUrl=str(product_doc.get("product_url", "")) if product_doc.get("product_url") else None,
            tags=[],
            productDetails=None,
            aboutThisItem=None,
            colorOptions=None,
            sizeOptions=None,
        )
    except Exception as e:
        print(f"[MongoDB Reader] 轉換產品失敗: {e}")
        raise


def get_products_from_mongodb(
    skip: int = 0,
    limit: int = 20,
    platform: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    status: str = "active"
) -> List[ProductResponse]:
    """從 MongoDB 獲取產品列表"""
    db = mongodb.connect()
    if db is None:
        print("MongoDB 未設定，返回空列表")
        return []
    
    try:
        products_collection = db["products"]
        
        # 構建查詢條件
        query = {}
        
        # 狀態過濾（MongoDB 中 status 為 "draft"，但我們返回時轉為 "active"）
        # 實際上我們返回所有數據，因為都是爬取的最新數據
        
        # 平台過濾
        if platform:
            query["platform"] = platform
        
        # 分類過濾
        if category:
            query["categories"] = {"$in": [category]}
        
        # 搜索過濾
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # 執行查詢
        cursor = products_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        products = list(cursor)
        
        # 轉換為響應格式
        result = []
        for product_doc in products:
            try:
                response = _mongo_product_to_response(product_doc)
                result.append(response)
            except Exception as e:
                print(f"[MongoDB Reader] 跳過產品: {e}")
                continue
        
        return result
        
    except Exception as e:
        print(f"[MongoDB Reader] 獲取產品失敗: {e}")
        return []
    finally:
        mongodb.close()


def get_product_by_id_from_mongodb(product_id: str) -> Optional[ProductResponse]:
    """從 MongoDB 根據 ID 獲取單個產品"""
    db = mongodb.connect()
    if db is None:
        return None
    
    try:
        products_collection = db["products"]
        
        # 嘗試通過 content_hash 查找
        if product_id.startswith("prod-"):
            hash_part = product_id.replace("prod-", "")
            product_doc = products_collection.find_one({"content_hash": {"$regex": f"^{hash_part}"}})
        else:
            # 嘗試通過 _id 查找
            from bson import ObjectId
            try:
                product_doc = products_collection.find_one({"_id": ObjectId(product_id)})
            except:
                product_doc = None
        
        if product_doc:
            return _mongo_product_to_response(product_doc)
        
        return None
        
    except Exception as e:
        print(f"[MongoDB Reader] 獲取產品失敗: {e}")
        return None
    finally:
        mongodb.close()


def get_products_stats_from_mongodb() -> Dict[str, Any]:
    """從 MongoDB 獲取產品統計信息"""
    db = mongodb.connect()
    if db is None:
        return {"totalProducts": 0, "activeProducts": 0, "platforms": {}}
    
    try:
        products_collection = db["products"]
        
        total_count = products_collection.count_documents({})
        active_count = total_count  # MongoDB 中所有產品都是 active
        
        # 按平台統計
        platforms = {}
        pipeline = [
            {"$group": {"_id": "$platform", "count": {"$sum": 1}}}
        ]
        for result in products_collection.aggregate(pipeline):
            platform = result.get("_id") or "unknown"
            platforms[platform] = result.get("count", 0)
        
        return {
            "totalProducts": total_count,
            "activeProducts": active_count,
            "platforms": platforms
        }
    except Exception as e:
        print(f"[MongoDB Reader] 獲取統計失敗: {e}")
        return {"totalProducts": 0, "activeProducts": 0, "platforms": {}}
    finally:
        mongodb.close()

