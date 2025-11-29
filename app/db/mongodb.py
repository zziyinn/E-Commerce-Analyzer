from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from typing import Optional


class MongoDBClient:
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.async_client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.async_database = None

    def connect(self):
        """建立同步 MongoDB 連線"""
        if not settings.mongodb_url:
            return None
        
        try:
            # 创建 MongoDB 客户端
            self.client = MongoClient(
                settings.mongodb_url, 
                serverSelectionTimeoutMS=5000,
                tlsAllowInvalidCertificates=True  # 仅用于开发环境
            )
            self.database = self.client[settings.mongodb_database]
            # 测试连接
            self.client.admin.command('ping')
            return self.database
        except Exception as e:
            print(f"MongoDB 连接错误: {e}")
            return None

    def connect_async(self):
        """建立異步 MongoDB 連線"""
        if not settings.mongodb_url:
            return None
            
        self.async_client = AsyncIOMotorClient(settings.mongodb_url)
        self.async_database = self.async_client[settings.mongodb_database]
        return self.async_database

    def close(self):
        """關閉連線"""
        if self.client:
            self.client.close()
        if self.async_client:
            self.async_client.close()


# 全域實例
mongodb = MongoDBClient()
