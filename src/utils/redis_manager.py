import aioredis


class RedisManager:
    _pool = None

    @classmethod
    async def get_connection(cls):
        if cls._pool is None:
            cls._pool = await aioredis.from_url("redis://localhost")
        return cls._pool

    @classmethod
    async def close_connection(cls):
        if cls._pool is not None:
            cls._pool.close()
            await cls._pool.wait_closed()
            cls._pool = None
