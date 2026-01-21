from .settings import Settings
from redis.asyncio import Redis


class RedisClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def get_client(self):
        return Redis(
            host=self.settings.redis_host,
            port=self.settings.redis_port,
            db=self.settings.redis_db,
            decode_responses=self.settings.decode_responses,
        )
