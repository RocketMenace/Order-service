from redis.asyncio import Redis, RedisError
from uuid import UUID
from ..exceptions.cache_exc import CacheClientException
from app.infrastructure.config.settings import Settings


class RedisRepository:
    def __init__(self, client: Redis, settings: Settings):
        self.client = client
        self.settings = settings

    async def exists(self, key: UUID) -> bool:
        async with self.client:
            try:
                return bool(await self.client.exists(str(key)))
            except RedisError:
                raise CacheClientException

    async def save(self, key: UUID, value: str) -> None:
        async with self.client:
            try:
                await self.client.set(
                    name=str(key), value=value, ex=self.settings.cache_ttl
                )
            except RedisError:
                raise CacheClientException
