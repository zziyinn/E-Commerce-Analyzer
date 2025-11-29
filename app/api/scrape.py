"""
搜索和爬取 API 端點
接收搜索關鍵詞，使用 BeautifulSoup 爬取數據並存儲到 MongoDB
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.scrapers.beautifulsoup_scraper import BeautifulSoupScraper
from app.services.mongodb_writer import bulk_upsert_products_mongodb
from app.services.query_history import save_query_history, cleanup_old_queries, get_query_by_keyword, get_products_by_query_keyword
from app.services.mongodb_reader import ProductResponse

router = APIRouter(prefix="/api/scrape", tags=["scrape"])


class ScrapeRequest(BaseModel):
    """爬取請求模型"""
    search_terms: List[str]  # 搜索關鍵詞列表
    fetch_details: bool = False  # 是否獲取商品詳情頁面
    max_products: int = 20  # 最大爬取商品數量


class ScrapeResponse(BaseModel):
    """爬取響應模型"""
    success: bool
    message: str
    products_count: int
    run_id: str
    products: List[ProductResponse] = []


def _beautifulsoup_to_product_with_categories(products: List[Dict[str, Any]], source_url: str = "https://www.amazon.com/") -> List:
    """將 BeautifulSoup 爬取的產品轉換為 ProductWithCategories 格式"""
    from app.schemas.product import ProductIn, CategoryIn, ProductWithCategories
    import hashlib
    
    result = []
    
    for p in products:
        if not p.get('name'):
            continue
        
        # 計算 content_hash
        core_values = [
            p.get('name'),
            p.get('price'),
            str(p.get('rating') or ''),
            p.get('review_count'),
            p.get('image_url'),
            p.get('product_url'),
            p.get('description'),
            source_url,
        ]
        hasher = hashlib.sha256()
        for v in core_values:
            hasher.update((str(v) or "").encode("utf-8"))
            hasher.update(b"\x1f")
        content_hash = hasher.hexdigest()
        
        # 解析 review_count
        review_count_text = p.get('review_count') or p.get('review_count_text')
        review_count = None
        if review_count_text:
            try:
                review_count = int(str(review_count_text).replace(",", "").strip())
            except:
                pass
        
        # 創建 ProductIn
        product_in = ProductIn(
            name=p.get('name'),
            price=p.get('price'),
            rating=p.get('rating'),
            review_count_text=review_count_text,
            review_count=review_count,
            image_url=p.get('image_url'),
            product_url=p.get('product_url'),
            description=p.get('description'),
            source_url=source_url,
            content_hash=content_hash,
            platform="amazon",  # BeautifulSoup 爬蟲默認爬取 Amazon
        )
        
        # 提取分類（從 category_path 或其他字段）
        categories = []
        if p.get('category_path'):
            # 從 category_path 提取分類
            parts = [part.strip() for part in p.get('category_path', '').split('>') if part.strip()]
            for part in parts[:3]:  # 最多取前3個分類
                if part and part.lower() != 'home':
                    categories.append(CategoryIn(name=part, source_url=source_url))
        
        # 如果沒有分類，使用默認分類
        if not categories:
            categories.append(CategoryIn(name="General", source_url=source_url))
        
        result.append(ProductWithCategories(product=product_in, categories=categories))
    
    return result


@router.post("/", response_model=ScrapeResponse)
async def scrape_products(request: ScrapeRequest):
    """
    搜索並爬取商品
    如果該關鍵詞之前查詢過，直接返回上次的結果
    
    Args:
        request: 爬取請求，包含搜索關鍵詞列表
    """
    try:
        # 限制搜索關鍵詞數量（避免過度爬取）
        search_terms = request.search_terms[:5]  # 最多5個關鍵詞
        
        # 檢查是否有該關鍵詞的歷史查詢（使用第一個關鍵詞）
        query_keyword = search_terms[0] if search_terms else "unknown"
        existing_query = get_query_by_keyword(query_keyword)
        
        if existing_query and existing_query.get("run_id"):
            # 找到歷史查詢，直接返回上次的結果
            print(f"[Scrape API] 找到關鍵詞 '{query_keyword}' 的歷史查詢，返回上次結果")
            run_id = existing_query["run_id"]
            
            # 獲取該查詢的產品
            mongo_products = get_products_by_query_keyword(query_keyword)
            
            # 轉換為響應格式
            from app.services.mongodb_reader import _mongo_product_to_response
            response_products = []
            for mongo_product in mongo_products:
                try:
                    # 确保 mongo_product 是字典格式
                    if not isinstance(mongo_product, dict):
                        continue
                    response = _mongo_product_to_response(mongo_product)
                    response_products.append(response)
                except Exception as e:
                    print(f"[Scrape API] 轉換產品失敗: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            return ScrapeResponse(
                success=True,
                message=f"Returned cached results for '{query_keyword}' ({len(response_products)} products)",
                products_count=len(response_products),
                run_id=run_id,
                products=response_products
            )
        
        # 沒有歷史查詢，執行爬取
        # 生成 run_id
        run_id = f"scrape-{uuid.uuid4().hex[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 初始化爬蟲
        scraper = BeautifulSoupScraper()
        
        # 爬取商品
        print(f"[Scrape API] 開始爬取，關鍵詞: {search_terms}")
        products = scraper.scrape_products(
            search_terms=search_terms,
            fetch_details=request.fetch_details
        )
        
        # 限制商品數量
        if len(products) > request.max_products:
            products = products[:request.max_products]
        
        print(f"[Scrape API] 爬取到 {len(products)} 個商品")
        
        if not products:
            return ScrapeResponse(
                success=False,
                message="No products scraped",
                products_count=0,
                run_id=run_id,
                products=[]
            )
        
        # 轉換為標準格式
        source_url = "https://www.amazon.com/"
        product_with_categories = _beautifulsoup_to_product_with_categories(products, source_url)
        
        # 存儲到 MongoDB
        print(f"[Scrape API] 開始寫入 MongoDB...")
        mongo_count = bulk_upsert_products_mongodb(product_with_categories, run_id=run_id)
        print(f"[Scrape API] 成功寫入 {mongo_count} 個商品到 MongoDB")
        
        # 保存查詢歷史（使用第一個關鍵詞作為查詢關鍵詞）
        query_keyword = search_terms[0] if search_terms else "unknown"
        save_query_history(query_keyword, run_id, mongo_count)
        
        # 自動清理舊數據（保留最近5次查詢）
        cleanup_old_queries(keep_count=5)
        
        # 轉換為 API 響應格式
        response_products = []
        for item in product_with_categories:
            try:
                # 創建一個臨時的 Product 對象用於轉換
                # 由於我們直接從 BeautifulSoup 獲取數據，需要手動構建響應
                product = item.product
                price = 0.0
                if product.price:
                    import re
                    cleaned = re.sub(r'[$,]', '', str(product.price))
                    try:
                        price = float(cleaned)
                    except:
                        pass
                
                # 計算利潤率和競爭度（使用與 mongodb_reader.py 相同的邏輯）
                from app.services.mongodb_reader import _calculate_margin_rate, _calculate_competition_score, _get_competition_level
                
                margin_rate = _calculate_margin_rate(price)
                competition_score = _calculate_competition_score(product.review_count, product.rating)
                competition_level = _get_competition_level(competition_score)
                
                # 獲取分類
                category = "General"
                if item.categories:
                    category = item.categories[0].name
                
                response_products.append(ProductResponse(
                    id=f"prod-{product.content_hash[:12]}",
                    title=product.name,
                    platform="amazon",
                    price=price,
                    formattedPrice=product.price or f"${price:.2f}",
                    marginRate=round(margin_rate, 2),
                    competitionScore=round(competition_score, 2),
                    competitionLevel=competition_level,
                    category=category,
                    imageUrl=str(product.image_url) if product.image_url else None,
                    description=product.description,
                    rating=product.rating,
                    reviewCount=product.review_count,
                    productUrl=str(product.product_url) if product.product_url else None,
                    tags=[],
                    productDetails=None,
                    aboutThisItem=None,
                    colorOptions=None,
                    sizeOptions=None,
                ))
            except Exception as e:
                print(f"[Scrape API] 轉換商品時出錯: {e}")
                continue
        
        return ScrapeResponse(
            success=True,
            message=f"Successfully scraped {len(response_products)} products and stored to MongoDB",
            products_count=len(response_products),
            run_id=run_id,
            products=response_products
        )
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        print(f"[Scrape API] 錯誤: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {error_msg}")


@router.get("/status/{run_id}")
async def get_scrape_status(run_id: str):
    """獲取爬取任務狀態（未來可以實現任務隊列）"""
    # 目前簡單實現，未來可以擴展為任務隊列
    return {
        "run_id": run_id,
        "status": "completed",
        "message": "Scraping task completed"
    }

