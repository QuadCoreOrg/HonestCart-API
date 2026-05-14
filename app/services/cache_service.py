import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional

import redis.asyncio as redis

from app.config import settings
from app.models.analysis import AnalysisResult


class CacheService:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.local_cache: dict[str, tuple[datetime, str]] = {}  # Fallback

    async def connect(self):
        try:
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
            await self.redis.ping()
        except Exception as e:
            print(f"Redis bağlanamadı, lokal cache kullanılıyor: {e}")
            self.redis = None

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    def _hash_url(self, url: str) -> str:
        # Normalize URL ve hashle
        normalized = url.strip().lower()
        return hashlib.sha256(normalized.encode()).hexdigest()

    async def get(self, url: str) -> Optional[AnalysisResult]:
        url_hash = self._hash_url(url)

        # Redis'ten dene
        if self.redis:
            try:
                cached = await self.redis.get(f"analysis:{url_hash}")
                if cached:
                    data = json.loads(cached)
                    return AnalysisResult(**data)
            except Exception as e:
                print(f"Redis get error: {e}")

        # Fallback: local cache
        if url_hash in self.local_cache:
            expiry, data = self.local_cache[url_hash]
            if datetime.now() < expiry:
                return AnalysisResult(**json.loads(data))

        return None

    async def set(self, url: str, result: AnalysisResult) -> None:
        url_hash = self._hash_url(url)
        data = result.model_dump_json()
        ttl = settings.cache_ttl_hours * 3600

        # Redis'e yaz
        if self.redis:
            try:
                await self.redis.setex(f"analysis:{url_hash}", ttl, data)
            except Exception as e:
                print(f"Redis set error: {e}")

        # Fallback: local cache
        expiry = datetime.now() + timedelta(hours=settings.cache_ttl_hours)
        self.local_cache[url_hash] = (expiry, data)


cache_service = CacheService()