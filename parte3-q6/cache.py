from redis import RedisError
from redis.asyncio import Redis

from config import env

redis = Redis.from_url(env("REDIS_URL"), decode_responses=True)


async def ler_cache(chave):
    try:
        return await redis.get(chave)
    except RedisError:
        return None


async def salvar_cache(chave, valor):
    try:
        await redis.set(chave, valor, ex=60)
    except RedisError:
        pass


async def invalidar_listas_de_produtos():
    try:
        chaves = [chave async for chave in redis.scan_iter("produtos:list:*")]
        if chaves:
            await redis.delete(*chaves)
    except RedisError:
        pass
