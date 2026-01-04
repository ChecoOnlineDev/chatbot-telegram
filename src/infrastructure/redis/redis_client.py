import redis

class RedisProvider:
    """Provee la instancia de conexión a Redis"""
    _pool: redis.ConnectionPool | None = None

    @classmethod
    def get_connection(cls) -> redis.Redis:
        if cls._pool is None:
            from src.infrastructure.redis.redis_configuration import redis_settings
            cls._pool = redis.ConnectionPool(
                host=redis_settings.REDIS_HOST,
                port=redis_settings.REDIS_PORT,
                db=redis_settings.REDIS_DB,
                password=redis_settings.REDIS_PASSWORD,
                decode_responses=True # Crucial para no lidiar con bytes
            )
        return redis.Redis(connection_pool=cls._pool)