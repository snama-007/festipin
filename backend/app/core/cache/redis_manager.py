"""
Redis Cache Manager with Connection Pooling
Optimized for high performance and reliability
"""

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from typing import Optional, Any, Union
import json
import pickle
import logging
from functools import wraps
import asyncio
from datetime import timedelta

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Redis manager with connection pooling, error handling, and automatic fallback
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 50,
        socket_timeout: int = 5,
        socket_connect_timeout: int = 5,
    ):
        self.pool = ConnectionPool(
            host=host,
            port=port,
            db=db,
            password=password,
            max_connections=max_connections,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            decode_responses=False,  # We handle encoding/decoding
        )
        self.client: Optional[redis.Redis] = None
        self.is_available = False

    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.Redis(connection_pool=self.pool)
            await self.client.ping()
            self.is_available = True
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.is_available = False

    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            await self.pool.disconnect()
            logger.info("Redis connection closed")

    async def get(
        self,
        key: str,
        default: Any = None,
        deserialize: bool = True
    ) -> Optional[Any]:
        """
        Get value from cache with automatic deserialization
        Falls back gracefully if Redis is unavailable
        """
        if not self.is_available:
            return default

        try:
            value = await self.client.get(key)
            if value is None:
                return default

            if deserialize:
                try:
                    # Try JSON first (faster)
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    # Fall back to pickle
                    return pickle.loads(value)
            return value

        except Exception as e:
            logger.warning(f"Redis GET error for key '{key}': {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[Union[int, timedelta]] = None,
        serialize: bool = True
    ) -> bool:
        """
        Set value in cache with automatic serialization
        """
        if not self.is_available:
            return False

        try:
            if serialize:
                # Try JSON first (faster and more compatible)
                try:
                    serialized_value = json.dumps(value)
                except (TypeError, ValueError):
                    # Fall back to pickle for complex objects
                    serialized_value = pickle.dumps(value)
            else:
                serialized_value = value

            if ttl:
                if isinstance(ttl, timedelta):
                    ttl = int(ttl.total_seconds())
                await self.client.setex(key, ttl, serialized_value)
            else:
                await self.client.set(key, serialized_value)

            return True

        except Exception as e:
            logger.warning(f"Redis SET error for key '{key}': {e}")
            return False

    async def delete(self, *keys: str) -> int:
        """Delete keys from cache"""
        if not self.is_available or not keys:
            return 0

        try:
            return await self.client.delete(*keys)
        except Exception as e:
            logger.warning(f"Redis DELETE error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.is_available:
            return False

        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Redis EXISTS error for key '{key}': {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter"""
        if not self.is_available:
            return None

        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.warning(f"Redis INCR error for key '{key}': {e}")
            return None

    async def set_hash(self, key: str, mapping: dict, ttl: Optional[int] = None) -> bool:
        """Set hash (dictionary)"""
        if not self.is_available:
            return False

        try:
            # Serialize complex values
            serialized_mapping = {}
            for k, v in mapping.items():
                try:
                    serialized_mapping[k] = json.dumps(v)
                except (TypeError, ValueError):
                    serialized_mapping[k] = pickle.dumps(v)

            await self.client.hset(key, mapping=serialized_mapping)

            if ttl:
                await self.client.expire(key, ttl)

            return True

        except Exception as e:
            logger.warning(f"Redis HSET error for key '{key}': {e}")
            return False

    async def get_hash(self, key: str, field: Optional[str] = None) -> Optional[Any]:
        """Get hash or hash field"""
        if not self.is_available:
            return None

        try:
            if field:
                value = await self.client.hget(key, field)
                if value:
                    try:
                        return json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        return pickle.loads(value)
                return None
            else:
                mapping = await self.client.hgetall(key)
                result = {}
                for k, v in mapping.items():
                    try:
                        result[k.decode()] = json.loads(v)
                    except (json.JSONDecodeError, TypeError):
                        result[k.decode()] = pickle.loads(v)
                return result

        except Exception as e:
            logger.warning(f"Redis HGET error for key '{key}': {e}")
            return None

    async def add_to_list(self, key: str, *values: Any, ttl: Optional[int] = None) -> bool:
        """Add values to list"""
        if not self.is_available:
            return False

        try:
            serialized_values = []
            for value in values:
                try:
                    serialized_values.append(json.dumps(value))
                except (TypeError, ValueError):
                    serialized_values.append(pickle.dumps(value))

            await self.client.rpush(key, *serialized_values)

            if ttl:
                await self.client.expire(key, ttl)

            return True

        except Exception as e:
            logger.warning(f"Redis RPUSH error for key '{key}': {e}")
            return False

    async def get_list(self, key: str, start: int = 0, end: int = -1) -> list:
        """Get list range"""
        if not self.is_available:
            return []

        try:
            values = await self.client.lrange(key, start, end)
            result = []
            for value in values:
                try:
                    result.append(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    result.append(pickle.loads(value))
            return result

        except Exception as e:
            logger.warning(f"Redis LRANGE error for key '{key}': {e}")
            return []


# Global Redis manager instance
redis_manager = RedisManager()


def cached(
    ttl: Union[int, timedelta] = 300,
    key_prefix: str = "",
    skip_on_error: bool = True
):
    """
    Decorator for caching function results

    Usage:
        @cached(ttl=600, key_prefix="motif:scene")
        async def get_scene(scene_id: str):
            return expensive_operation(scene_id)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}"

            # Add arguments to key
            if args:
                cache_key += ":" + ":".join(str(arg) for arg in args)
            if kwargs:
                cache_key += ":" + ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))

            # Try to get from cache
            cached_result = await redis_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_result

            logger.debug(f"Cache MISS: {cache_key}")

            # Execute function
            try:
                result = await func(*args, **kwargs)

                # Cache the result
                await redis_manager.set(cache_key, result, ttl=ttl)

                return result

            except Exception as e:
                if skip_on_error:
                    logger.error(f"Function execution error (cache skipped): {e}")
                    raise
                else:
                    logger.error(f"Function execution error: {e}")
                    raise

        return wrapper
    return decorator
