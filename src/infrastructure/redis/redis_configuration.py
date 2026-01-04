from pydantic_settings import BaseSettings #type: ignore

class Settings(BaseSettings):
    # Configuración de Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    SESSION_TTL: int = 3600  # 1 hora

    class Config:
        env_file = ".env"

redis_settings = Settings()