from pydantic_settings import BaseSettings #type: ignore
import redis

class Settings(BaseSettings):
    # Configuración de Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    SESSION_TTL: int = 3600  # 1 hora

    class Config:
        env_file = ".env"
        extra = "ignore"

redis_settings = Settings()

def get_redis_client():
    return redis.Redis(
        host=redis_settings.REDIS_HOST,
        port=redis_settings.REDIS_PORT,
        db=redis_settings.REDIS_DB,
        password=redis_settings.REDIS_PASSWORD,
        decode_responses=True
    )