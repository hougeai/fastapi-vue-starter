import secrets  # 用于生成安全的随机验证码，不可预测
import urllib
import hashlib
from typing import Tuple
from .redis_client import redis, set_cache, get_cache, delete_cache
from .config import settings
from .log import logger


# 验证码管理器-Redis
class RedisManager:
    def __init__(self):
        pass

    async def generate_phone_code(self, phone: str, expires_in: int = 10) -> str:
        """
        为指定手机号生成验证码
        :param phone: 目标手机号
        :param expires_in: 过期时间（分钟）
        :return: 6位数字验证码
        """
        # 检查 Redis 中是否已经存在该手机号的验证码
        existing_code = await get_cache(f'phone_code:{phone}')
        if existing_code:
            return False, '验证码仍在有效期内，请使用上次发送的验证码。'

        # 生成6位随机数字验证码
        code = ''.join(secrets.choice('0123456789') for _ in range(6))

        # 发送短信
        text = f'【{settings.SMS_PREFIX}】验证码：{code}，{expires_in}分钟内有效。如非本人操作，请忽略本短信。'
        success, msg = True, text
        if success:
            # 在Redis中存储验证码信息
            redis_key = f'phone_code:{phone}'
            await set_cache(redis_key, code, expires_in * 60)
        return success, msg

    async def verify_phone_code(self, phone: str, code: str) -> Tuple[bool, str]:
        """
        验证手机验证码
        :param phone: 目标手机号
        :param code: 待验证的验证码
        :return: (是否验证成功, 提示消息)
        """
        # 获取尝试次数
        attempt_key = f'phone_attempt:{phone}'
        attempts = await get_cache(attempt_key)

        # 如果尝试次数超过限制
        if attempts and int(attempts) >= 10:
            return False, '验证码尝试次数过多，请稍后再试'

        # 验证码验证逻辑
        redis_key = f'phone_code:{phone}'
        stored_code = await get_cache(redis_key)

        if not stored_code:
            return False, '请点击发送验证码'

        # 检查验证码是否匹配
        if stored_code != code:
            await redis.incr(attempt_key)  # 如果键不存在，会创建一个值为 0 的键，否则加 1，并返回新值
            # 设置尝试次数的过期时间
            await redis.expire(attempt_key, 60)
            return False, '验证码错误'

        # 验证成功，清除相关的Redis键
        await delete_cache(redis_key)
        await delete_cache(attempt_key)
        return True, '验证成功'
