"""
查询历史管理服务
记录每次查询，保留最近5次查询的数据，自动清理旧数据
"""

from app.db.mongodb import mongodb
from datetime import datetime
from typing import List, Dict, Optional


def save_query_history(query_keyword: str, run_id: str, product_count: int) -> Dict:
    """保存查询历史记录"""
    db = mongodb.connect()
    if db is None:
        print("MongoDB 未設定，跳過查詢歷史記錄")
        return {}
    
    try:
        history_collection = db["query_history"]
        
        history_doc = {
            "query_keyword": query_keyword,
            "run_id": run_id,
            "product_count": product_count,
            "created_at": datetime.utcnow()
        }
        
        result = history_collection.insert_one(history_doc)
        print(f"[Query History] 保存查詢歷史: {query_keyword} -> {run_id}")
        
        # 清理旧数据（保留最近5次）
        cleanup_old_queries(keep_count=5)
        
        return history_doc
    except Exception as e:
        print(f"[Query History] 保存失敗: {e}")
        return {}
    finally:
        mongodb.close()


def cleanup_old_queries(keep_count: int = 5) -> int:
    """清理旧的查询数据，只保留最近 N 次查询"""
    db = mongodb.connect()
    if db is None:
        return 0
    
    try:
        history_collection = db["query_history"]
        products_collection = db["products"]
        
        # 获取所有历史记录，按时间倒序
        all_history = list(history_collection.find().sort("created_at", -1))
        
        if len(all_history) <= keep_count:
            print(f"[Query History] 查詢記錄數 ({len(all_history)}) 不超過保留數 ({keep_count})，無需清理")
            return 0
        
        # 需要删除的历史记录（最旧的）
        to_delete = all_history[keep_count:]
        deleted_count = 0
        
        for history in to_delete:
            run_id = history.get("run_id")
            if run_id:
                # 删除该 run_id 对应的所有产品
                result = products_collection.delete_many({"run_id": run_id})
                deleted_products = result.deleted_count
                deleted_count += deleted_products
                print(f"[Query History] 刪除 run_id {run_id} 的 {deleted_products} 個產品")
            
            # 删除历史记录
            history_collection.delete_one({"_id": history["_id"]})
            print(f"[Query History] 刪除查詢歷史: {history.get('query_keyword')} ({run_id})")
        
        print(f"[Query History] 清理完成，刪除了 {len(to_delete)} 次查詢的數據，共 {deleted_count} 個產品")
        return deleted_count
        
    except Exception as e:
        print(f"[Query History] 清理失敗: {e}")
        return 0
    finally:
        mongodb.close()


def get_recent_queries(limit: int = 10) -> List[Dict]:
    """获取最近的查询记录"""
    db = mongodb.connect()
    if db is None:
        return []
    
    try:
        history_collection = db["query_history"]
        queries = list(history_collection.find().sort("created_at", -1).limit(limit))
        
        # 转换为可序列化的格式
        result = []
        for q in queries:
            result.append({
                "query_keyword": q.get("query_keyword"),
                "run_id": q.get("run_id"),
                "product_count": q.get("product_count"),
                "created_at": q.get("created_at").isoformat() if q.get("created_at") else None
            })
        
        return result
    except Exception as e:
        print(f"[Query History] 獲取查詢歷史失敗: {e}")
        return []
    finally:
        mongodb.close()


def get_query_count() -> int:
    """获取当前查询记录总数"""
    db = mongodb.connect()
    if db is None:
        return 0
    
    try:
        history_collection = db["query_history"]
        return history_collection.count_documents({})
    except Exception as e:
        print(f"[Query History] 獲取查詢數量失敗: {e}")
        return 0
    finally:
        mongodb.close()


def get_query_by_keyword(query_keyword: str) -> Optional[Dict]:
    """根据查询关键词获取最近的查询记录"""
    db = mongodb.connect()
    if db is None:
        return None
    
    try:
        history_collection = db["query_history"]
        # 查找相同关键词的最近一次查询
        query = history_collection.find_one(
            {"query_keyword": query_keyword},
            sort=[("created_at", -1)]
        )
        
        if query:
            return {
                "query_keyword": query.get("query_keyword"),
                "run_id": query.get("run_id"),
                "product_count": query.get("product_count"),
                "created_at": query.get("created_at")
            }
        return None
    except Exception as e:
        print(f"[Query History] 獲取查詢記錄失敗: {e}")
        return None
    finally:
        mongodb.close()


def get_products_by_query_keyword(query_keyword: str) -> List[Dict]:
    """根据查询关键词获取该查询的所有产品"""
    db = mongodb.connect()
    if db is None:
        return []
    
    try:
        # 先找到该关键词的查询记录
        query_record = get_query_by_keyword(query_keyword)
        if not query_record or not query_record.get("run_id"):
            return []
        
        run_id = query_record["run_id"]
        products_collection = db["products"]
        
        # 获取该 run_id 的所有产品
        products = list(products_collection.find({"run_id": run_id}))
        print(f"[Query History] 找到關鍵詞 '{query_keyword}' 的 {len(products)} 個產品")
        
        return products
    except Exception as e:
        print(f"[Query History] 獲取產品失敗: {e}")
        return []
    finally:
        mongodb.close()

