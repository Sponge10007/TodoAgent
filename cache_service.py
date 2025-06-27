#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存服务模块
仅使用内存缓存（Redis功能已注释）
"""

# Redis功能暂时注释
# try:
#     import redis
#     REDIS_AVAILABLE = True
# except ImportError:
#     redis = None
#     REDIS_AVAILABLE = False

import json
import os
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)

class CacheService:
    """缓存服务类 - 仅使用内存缓存"""
    
    def __init__(self):
        """初始化缓存服务"""
        # self.redis_client = None  # Redis功能已注释
        self.memory_cache = {}
        self.cache_stats = {"hits": 0, "misses": 0}
        
        logger.info("使用内存缓存模式")
        
        # Redis连接代码已注释
        # if REDIS_AVAILABLE:
        #     try:
        #         redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        #         self.redis_client = redis.from_url(redis_url, decode_responses=True)
        #         # 测试连接
        #         self.redis_client.ping()
        #         logger.info("Redis缓存连接成功")
        #     except Exception as e:
        #         logger.warning(f"Redis连接失败，使用内存缓存: {e}")
        #         self.redis_client = None  # 确保设置为None
        # else:
        #     logger.info("Redis模块未安装，使用内存缓存")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            # Redis代码已注释
            # if self.redis_client:
            #     value = self.redis_client.get(key)
            #     if value:
            #         self.cache_stats["hits"] += 1
            #         return json.loads(value)
            
            # 使用内存缓存
            if key in self.memory_cache:
                cache_item = self.memory_cache[key]
                if cache_item['expires_at'] > datetime.now():
                    self.cache_stats["hits"] += 1
                    return cache_item['value']
                else:
                    del self.memory_cache[key]
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"缓存获取失败: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存值"""
        try:
            # Redis代码已注释
            # if self.redis_client:
            #     self.redis_client.setex(key, ttl, json.dumps(value, default=str))
            #     return True
            
            # 使用内存缓存
            expires_at = datetime.now() + timedelta(seconds=ttl)
            self.memory_cache[key] = {
                'value': value,
                'expires_at': expires_at
            }
            return True
            
        except Exception as e:
            logger.error(f"缓存设置失败: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            # Redis代码已注释
            # if self.redis_client:
            #     self.redis_client.delete(key)
            
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            return True
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        count = 0
        try:
            # Redis代码已注释
            # if self.redis_client:
            #     keys = self.redis_client.keys(pattern)
            #     if keys:
            #         count = self.redis_client.delete(*keys)
            
            # 清理内存缓存
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
                count += 1
                
            return count
        except Exception as e:
            logger.error(f"批量缓存清除失败: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "hit_rate": round(hit_rate * 100, 2),
            "total_requests": total_requests,
            "memory_cache_size": len(self.memory_cache),
            "redis_connected": False,  # Redis功能已注释
            "redis_available": False,  # Redis功能已注释
            "cache_mode": "memory_only"  # 标识当前缓存模式
        }

# 全局缓存实例
cache_service = CacheService()

# 缓存装饰器
def cached(ttl: int = 3600, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            result = cache_service.get(cache_key)
            if result is not None:
                return result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator 