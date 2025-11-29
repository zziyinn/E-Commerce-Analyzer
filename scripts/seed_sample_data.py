#!/usr/bin/env python3
"""
预存示例数据到 MongoDB
用于在数据库为空时提供示例产品数据
"""

import sys
from pathlib import Path
from datetime import datetime
import uuid

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.mongodb import mongodb
from app.services.mongodb_writer import bulk_upsert_products_mongodb
from app.schemas.product import ProductWithCategories, Product, Category


def create_sample_products():
    """创建示例产品数据"""
    
    sample_products = [
        {
            "name": "Men's Classic T-Shirt - Cotton Comfort Fit",
            "price": 19.99,
            "rating": 4.5,
            "review_count_text": "2,345",
            "review_count": 2345,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08XYZ1234",
            "description": "Classic fit t-shirt made from 100% cotton. Comfortable and durable for everyday wear.",
            "platform": "amazon",
            "categories": ["Clothing", "Men's Clothing", "T-Shirts"]
        },
        {
            "name": "Wireless Bluetooth Earbuds - Noise Cancelling",
            "price": 79.99,
            "rating": 4.7,
            "review_count_text": "5,678",
            "review_count": 5678,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08ABC5678",
            "description": "Premium wireless earbuds with active noise cancellation and 30-hour battery life.",
            "platform": "amazon",
            "categories": ["Electronics", "Audio", "Headphones"]
        },
        {
            "name": "Women's Summer Dress - Floral Print",
            "price": 39.99,
            "rating": 4.3,
            "review_count_text": "1,234",
            "review_count": 1234,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08DEF9012",
            "description": "Beautiful floral print summer dress, perfect for casual and semi-formal occasions.",
            "platform": "amazon",
            "categories": ["Clothing", "Women's Clothing", "Dresses"]
        },
        {
            "name": "Smart Fitness Tracker - Waterproof",
            "price": 49.99,
            "rating": 4.6,
            "review_count_text": "3,456",
            "review_count": 3456,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08GHI3456",
            "description": "Advanced fitness tracker with heart rate monitor, sleep tracking, and 7-day battery.",
            "platform": "amazon",
            "categories": ["Electronics", "Wearables", "Fitness Trackers"]
        },
        {
            "name": "Leather Crossbody Bag - Handmade",
            "price": 89.99,
            "rating": 4.4,
            "review_count_text": "987",
            "review_count": 987,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08JKL7890",
            "description": "Genuine leather crossbody bag with adjustable strap and multiple compartments.",
            "platform": "amazon",
            "categories": ["Accessories", "Bags", "Handbags"]
        },
        {
            "name": "Stainless Steel Water Bottle - 32oz",
            "price": 24.99,
            "rating": 4.8,
            "review_count_text": "4,567",
            "review_count": 4567,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08MNO1234",
            "description": "Insulated stainless steel water bottle keeps drinks cold for 24 hours or hot for 12 hours.",
            "platform": "amazon",
            "categories": ["Home & Kitchen", "Kitchen", "Drinkware"]
        },
        {
            "name": "Yoga Mat - Extra Thick Non-Slip",
            "price": 29.99,
            "rating": 4.5,
            "review_count_text": "2,890",
            "review_count": 2890,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08PQR5678",
            "description": "Premium yoga mat with superior grip and cushioning for all types of yoga practice.",
            "platform": "amazon",
            "categories": ["Sports & Outdoors", "Exercise & Fitness", "Yoga"]
        },
        {
            "name": "LED Desk Lamp - Adjustable Brightness",
            "price": 34.99,
            "rating": 4.4,
            "review_count_text": "1,567",
            "review_count": 1567,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08STU9012",
            "description": "Modern LED desk lamp with 5 brightness levels and color temperature adjustment.",
            "platform": "amazon",
            "categories": ["Home & Kitchen", "Lighting", "Desk Lamps"]
        },
        {
            "name": "Portable Phone Charger - 20000mAh",
            "price": 39.99,
            "rating": 4.6,
            "review_count_text": "6,234",
            "review_count": 6234,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08VWX3456",
            "description": "High-capacity portable charger with fast charging technology and dual USB ports.",
            "platform": "amazon",
            "categories": ["Electronics", "Mobile Accessories", "Power Banks"]
        },
        {
            "name": "Organic Coffee Beans - Medium Roast",
            "price": 16.99,
            "rating": 4.7,
            "review_count_text": "3,123",
            "review_count": 3123,
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71X8NxQJZBL._AC_UL1500_.jpg",
            "product_url": "https://www.amazon.com/dp/B08XYZ7890",
            "description": "Premium organic coffee beans, medium roast, 12oz bag. Smooth and balanced flavor.",
            "platform": "amazon",
            "categories": ["Grocery", "Beverages", "Coffee"]
        }
    ]
    
    # 转换为 ProductWithCategories 格式
    products_with_categories = []
    run_id = f"seed-{uuid.uuid4().hex[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    for item in sample_products:
        # 创建 Product 对象
        product = Product(
            name=item["name"],
            price=item["price"],
            rating=item["rating"],
            review_count_text=item["review_count_text"],
            review_count=item["review_count"],
            image_url=item.get("image_url"),
            product_url=item["product_url"],
            description=item.get("description", ""),
            source_url=item.get("product_url"),
            platform=item["platform"],
            content_hash=f"sample-{uuid.uuid4().hex[:16]}"
        )
        
        # 创建 Category 对象列表
        categories = [Category(name=cat) for cat in item["categories"]]
        
        # 创建 ProductWithCategories
        product_with_categories = ProductWithCategories(
            product=product,
            categories=categories
        )
        
        products_with_categories.append(product_with_categories)
    
    return products_with_categories, run_id


def main():
    """主函数"""
    print("=== 预存示例数据到 MongoDB ===")
    
    # 检查 MongoDB 连接
    db = mongodb.connect()
    if db is None:
        print("❌ MongoDB 未配置，请检查 MONGODB_URL 环境变量")
        return
    
    print("✅ MongoDB 连接成功")
    
    # 检查是否已有数据
    products_collection = db["products"]
    existing_count = products_collection.count_documents({"status": "active"})
    
    if existing_count > 0:
        print(f"⚠️  数据库中已有 {existing_count} 个产品，是否继续添加示例数据？")
        response = input("输入 'yes' 继续，其他任意键取消: ")
        if response.lower() != 'yes':
            print("已取消")
            return
    
    # 创建示例数据
    print("📦 创建示例产品数据...")
    products_with_categories, run_id = create_sample_products()
    print(f"✅ 创建了 {len(products_with_categories)} 个示例产品")
    
    # 写入 MongoDB
    print("💾 写入 MongoDB...")
    try:
        affected = bulk_upsert_products_mongodb(products_with_categories, run_id=run_id)
        print(f"✅ 成功写入 {affected} 个产品到 MongoDB")
        print(f"📝 Run ID: {run_id}")
        
        # 更新状态为 active
        products_collection.update_many(
            {"run_id": run_id, "status": "draft"},
            {"$set": {"status": "active", "updated_at": datetime.utcnow()}}
        )
        print("✅ 产品状态已更新为 active")
        
    except Exception as e:
        print(f"❌ 写入失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        mongodb.close()
    
    print("\n🎉 完成！现在可以在前端看到示例产品了。")


if __name__ == "__main__":
    main()

