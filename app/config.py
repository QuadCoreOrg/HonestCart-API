from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    firecrawl_api_key: str
    gemini_api_key: str
    cache_ttl_hours: int = 6
    max_reviews_per_analysis: int = 200
    min_reviews_required: int = 10
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = ConfigDict(env_file=".env")


settings = Settings()