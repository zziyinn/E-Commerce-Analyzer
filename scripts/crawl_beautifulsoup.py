#!/usr/bin/env python3
"""
BeautifulSoup 爬蟲主腳本
"""

import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.scrapers import BeautifulSoupScraper
from app.pipelines.amazon_adapter import extract_products_with_categories
from app.services.mongodb_writer import bulk_upsert_products_mongodb
from app.services.query_history import save_query_history, cleanup_old_queries


def main():
    """主函數"""
    print("=== BeautifulSoup Amazon 爬蟲 ===")
    
    # 初始化爬蟲
    scraper = BeautifulSoupScraper()
    
    # 搜索詞列表
    search_terms = [
        "men's t-shirt",
        "women's dress", 
        "jeans",
        "sneakers",
        "jacket"
    ]
    
    # 爬取商品
    print("開始爬取商品...")
    products = scraper.scrape_products(search_terms)
    print(f"爬取到 {len(products)} 個商品")
    
    # 爬取分類
    print("開始爬取分類...")
    categories = scraper.scrape_categories()
    print(f"爬取到 {len(categories)} 個分類")
    
    # 保存結果
    result_data = {
        "products": products,
        "categories": categories
    }
    
    filepath = scraper.save_results(result_data, "beautifulsoup_products.json")
    print(f"結果已保存到: {filepath}")
    
    # 轉換為數據庫格式並寫入 MongoDB
    if products:
        print("開始寫入 MongoDB...")
        
        # 創建兼容格式的數據
        class ResultWrapper:
            def __init__(self, data):
                self._data = data
            def model_dump(self, exclude_none=True, mode="json"):
                return {
                    "data": [{
                        "json": self._data,
                        "metadata": {"url": "https://www.amazon.com/"}
                    }]
                }
        
        result = ResultWrapper(result_data)
        
        # 轉換為標準格式
        data = extract_products_with_categories(result)
        
        # 生成 run_id
        import uuid
        from datetime import datetime
        run_id = f"run-beautifulsoup-{uuid.uuid4().hex[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 寫入 MongoDB
        mongo_affected = bulk_upsert_products_mongodb(data, run_id=run_id)
        print(f"Upsert {mongo_affected} products to MongoDB")
        
        # 保存查詢歷史（使用第一個搜索詞）
        if search_terms:
            query_keyword = search_terms[0]
            save_query_history(query_keyword, run_id, mongo_affected)
            cleanup_old_queries(keep_count=5)


if __name__ == "__main__":
    main()
