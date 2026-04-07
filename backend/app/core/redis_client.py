from redis.asyncio import Redis, ConnectionPool
from .config import settings
from .log import logger

pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    max_connections=settings.REDIS_POOL_SIZE,  # 最大连接数
    db=0,
    decode_responses=True,  # 自动将字节解码为字符串
)

redis = Redis(connection_pool=pool)


async def get_cache(key: str):
    try:
        value = await redis.get(key)
        # logger.info(f"成功获取缓存: {key}")
        return value
    except Exception as e:
        logger.error(f'获取缓存 {key} 失败: {e}')
        return None


async def delete_cache(key: str):
    try:
        await redis.delete(key)
        # logger.info(f"成功删除缓存: {key}" if result else f"缓存不存在: {key}")
    except Exception as e:
        logger.error(f'删除缓存 {key} 失败: {e}')


async def set_cache(
    key: str,
    value: str | bytes | int | float,
    ttl: int | None = None,
    nx: bool = False,
    xx: bool = False,
) -> bool:
    """
    Args:
        key:   缓存键
        value: 缓存值，支持 str / bytes / int / float
        ttl:   过期时间（秒），None 表示永不过期
        nx:    仅当 key 不存在时写入（SET IF NOT EXISTS）
        xx:    仅当 key 存在时写入（SET IF EXISTS）

    Returns:
        默认不带 NX 或 XX 条件时，总是会成功写入，返回 "OK"，不管 key 是否存在，都会覆盖旧值
        在使用 NX 或 XX 条件时，SET 才可能返回 None，表示“条件不满足”。
    """
    try:
        status = await redis.set(key, value, ex=ttl, nx=nx, xx=xx)
        if not status:
            logger.info(f'写入缓存未生效: {key} (条件不满足)')
    except Exception:
        logger.error(f'写入缓存失败: {key}')
