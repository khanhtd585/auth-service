
from functools import lru_cache

import redis.asyncio as redis
from typing import Optional

from common.setting import get_settings

setting = get_settings()

class AsyncRedisClient:
    """Async client để quản lý kết nối Redis"""
    
    def __init__(self):
        """
        Khởi tạo Async Redis client
        
        Args:
            host: Redis host (mặc định: localhost)
            port: Redis port (mặc định: 6379)
            db: Redis database number (mặc định: 0)
            decode_responses: Tự động decode responses thành string (mặc định: True)
        """
        self.host = setting.REDIS_HOST
        self.port = setting.REDIS_PORT
        self.db = setting.REDIS_DB
        self.decode_responses = setting.DECODE_RESPONSES
        self.client: Optional[redis.Redis] = None
        
    async def connect(self) -> redis.Redis:
        """Tạo kết nối Redis async"""
        if self.client is None:
            self.client = await redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=self.decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5
            )
        return self.client
    
    async def close(self):
        """Đóng kết nối Redis"""
        if self.client:
            await self.client.close()
            self.client = None
    
    async def ping(self) -> bool:
        """Kiểm tra kết nối Redis"""
        try:
            if self.client is None:
                await self.connect()
            return await self.client.ping()
        except redis.ConnectionError:
            return False
    
    async def get_client(self) -> redis.Redis:
        """Lấy Redis client instance"""
        if self.client is None:
            await self.connect()
        return self.client
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()


@lru_cache
def get_redis() -> AsyncRedisClient:
    """
    Function to get 'Settings' instance.
    Use 'lru_cache' so that 'Settings' is created only once
    """
    return AsyncRedisClient()
