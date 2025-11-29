"""
產品 API 端點
提供產品數據給前端
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from app.services.mongodb_reader import (
    get_products_from_mongodb,
    get_product_by_id_from_mongodb,
    get_products_stats_from_mongodb,
    ProductResponse
)

router = APIRouter(prefix="/api/products", tags=["products"])

# ProductResponse 定义在 app/services/mongodb_reader.py 中，避免循环导入

@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    status: str = Query("active", regex="^(active|draft|all)$"),
):
    """
    獲取產品列表（從 MongoDB 讀取）
    
    Args:
        skip: 跳過的記錄數
        limit: 返回的記錄數
        platform: 平台過濾（amazon, walmart, ebay 等）
        category: 分類過濾
        search: 搜索關鍵詞
        status: 狀態過濾（active, draft, all）- 目前 MongoDB 中所有數據都是 active
    """
    try:
        # 從 MongoDB 讀取數據
        products = get_products_from_mongodb(
            skip=skip,
            limit=limit,
            platform=platform,
            category=category,
            search=search,
            status=status
        )
        return products
    except Exception as e:
        import traceback
        print(f"Error in get_products: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get products list: {str(e)}")


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str):
    """
    獲取單個產品詳情（從 MongoDB 讀取）
    
    Args:
        product_id: 產品 ID（格式: prod-{hash} 或 MongoDB _id）
    """
    try:
        product = get_product_by_id_from_mongodb(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_product: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get product details: {str(e)}")


@router.get("/stats/summary")
def get_stats():
    """獲取產品統計信息（從 MongoDB 讀取）"""
    try:
        stats = get_products_stats_from_mongodb()
        return stats
    except Exception as e:
        import traceback
        print(f"Error in get_stats: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

