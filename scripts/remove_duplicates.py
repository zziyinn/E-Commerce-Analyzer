#!/usr/bin/env python3
"""
删除 MongoDB 中重复的产品
基于 product_url 和 name 去重，保留最新的
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.mongodb import mongodb
from collections import defaultdict

def remove_duplicate_products():
    """删除重复的产品，保留最新的"""
    db = mongodb.connect()
    if db is None:
        print("MongoDB 未設定，無法執行去重")
        return
    
    try:
        products_collection = db["products"]
        
        # 获取所有产品
        all_products = list(products_collection.find())
        print(f"總共有 {len(all_products)} 個產品")
        
        # 按 product_url 和 name 分组
        product_groups = defaultdict(list)
        for product in all_products:
            key = (
                product.get("product_url", ""),
                product.get("name", "")
            )
            if key[0] or key[1]:  # 至少有一个值
                product_groups[key].append(product)
        
        print(f"找到 {len(product_groups)} 個唯一產品組")
        
        # 统计重复
        duplicates_count = 0
        to_delete_ids = []
        
        for key, products in product_groups.items():
            if len(products) > 1:
                # 按 created_at 排序，保留最新的
                products_sorted = sorted(
                    products,
                    key=lambda x: x.get("created_at", x.get("updated_at")),
                    reverse=True
                )
                
                # 标记旧的要删除
                for product in products_sorted[1:]:
                    to_delete_ids.append(product["_id"])
                    duplicates_count += 1
        
        print(f"找到 {duplicates_count} 個重複產品需要刪除")
        
        if to_delete_ids:
            # 删除重复产品
            result = products_collection.delete_many({"_id": {"$in": to_delete_ids}})
            print(f"成功刪除 {result.deleted_count} 個重複產品")
        else:
            print("沒有重複產品需要刪除")
        
        # 统计最终数量
        final_count = products_collection.count_documents({})
        print(f"最終產品數量: {final_count}")
        
    except Exception as e:
        print(f"去重失敗: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mongodb.close()


if __name__ == "__main__":
    print("開始刪除重複產品...")
    remove_duplicate_products()
    print("去重完成！")

