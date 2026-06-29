import redis
import os
import json
import logging

logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

redis_client = None

def init_redis():
    """Инициализация подключения к Redis"""
    global redis_client
    
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5
        )
        # Проверка подключения
        redis_client.ping()
        logger.info("Successfully connected to Redis")
        return True
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return False

def get_cached_counter():
    """Получение счетчика из кэша"""
    if redis_client:
        try:
            value = redis_client.get("visit_counter")
            if value:
                return int(value)
        except Exception as e:
            logger.error(f"Error reading from Redis: {e}")
    return None

def set_cached_counter(value):
    """Сохранение счетчика в кэш"""
    if redis_client:
        try:
            redis_client.set("visit_counter", value, ex=3600)  # TTL 1 час
            return True
        except Exception as e:
            logger.error(f"Error writing to Redis: {e}")
    return False

def get_cached_static(key):
    """Получение статики из кэша"""
    if redis_client:
        try:
            value = redis_client.get(f"static:{key}")
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Error reading static from Redis: {e}")
    return None

def set_cached_static(key, value, ttl=300):
    """Сохранение статики в кэш"""
    if redis_client:
        try:
            redis_client.setex(f"static:{key}", ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Error writing static to Redis: {e}")
    return False