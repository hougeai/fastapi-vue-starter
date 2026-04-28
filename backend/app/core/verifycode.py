import secrets  # 用于生成安全的随机验证码，不可预测
import smtplib
from email.mime.text import MIMEText
from typing import Tuple
from .redis_client import redis, set_cache, get_cache, delete_cache
from .config import settings
from .log import logger


# 邮件管理器
class EmailManager:
    def __init__(self):
        # 邮件服务器配置
        self.email_host = settings.EMAIL_HOST
        self.email_port = settings.EMAIL_PORT
        self.email_user = settings.EMAIL_USER
        self.email_password = settings.EMAIL_PASSWORD
        self.sender = settings.EMAIL_SENDER
        # 初始化 SMTP 连接
        self.smtp = None
        self._connect()

    def _connect(self):
        """建立 SMTP 连接"""
        try:
            self.smtp = smtplib.SMTP_SSL(self.email_host, self.email_port, timeout=10)
            self.smtp.login(self.email_user, self.email_password)
        except Exception as e:
            logger.error(f'SMTP 连接失败：{e}')
            self.smtp = None

    def _ensure_connection(self):
        """确保 SMTP 连接有效"""
        if self.smtp is None:
            self._connect()
        else:
            try:
                self.smtp.noop()  # 检查连接是否仍然有效
            except smtplib.SMTPServerDisconnected:
                logger.warning('SMTP 连接已断开，正在重新连接...')
                self._connect()

    def send_email(self, email: str, text: str, subject: str = ''):
        max_retries = 3  # 最大重试次数
        for attempt in range(max_retries):
            # 确保连接有效
            self._ensure_connection()
            if self.smtp is None:
                return False, '无法建立 SMTP 连接'
            try:
                msg = MIMEText(text, 'plain', 'utf-8')
                msg['From'] = self.sender
                msg['To'] = email
                msg['Subject'] = subject
                message = msg.as_string()
                self.smtp.sendmail(self.sender, email, message)
                return True, '邮件已发送至您的邮箱'
            except Exception as e:
                # 关闭当前可能有问题的连接
                try:
                    self.smtp.quit()
                except Exception:
                    pass
                self.smtp = None
                if attempt < max_retries - 1:  # 如果不是最后一次尝试
                    logger.warning(f'第{attempt + 1}次发送失败：{e}，准备重试')
                    continue
                logger.error(f'邮件发送失败（已重试{max_retries}次）：{e}')
                return False, '邮件发送失败，请重试'

    def __del__(self):
        """对象销毁时关闭连接"""
        if self.smtp:
            try:
                self.smtp.quit()
            except Exception as e:
                logger.error(f'关闭 SMTP 连接时出错：{e}')

# 验证码管理器-Redis
class RedisManager:
    def __init__(self):
        self.email_manager = EmailManager()
        self.logo_name = settings.LOGO_NAME

    async def generate_code(self, email: str, expires_in: int = 10) -> str:
        """
        为指定邮箱生成验证码
        :param email: 目标邮箱
        :param expires_in: 过期时间（分钟）
        :return: 6位数字验证码
        """
        # 生成6位随机数字验证码
        code = ''.join(secrets.choice('0123456789') for _ in range(6))

        # 发送邮件
        text = f'您的验证码为：{code}，有效期为{expires_in}分钟。'
        subject = f'[no-reply] {self.logo_name} 验证码'
        success, msg = self.email_manager.send_email(email, text, subject)
        if success:
            # 在Redis中存储验证码信息，使用email作为key
            redis_key = f'verify_code:{email}'
            await set_cache(redis_key, code, expires_in * 60)
        return success, msg

    async def verify_code(self, email: str, code: str) -> Tuple[bool, str]:
        """
        验证邮箱验证码
        :param email: 目标邮箱
        :param code: 待验证的验证码
        :return: (是否验证成功, 提示消息)
        """
        # 获取尝试次数
        attempt_key = f'verify_attempt:{email}'
        attempts = await get_cache(attempt_key)

        # 如果尝试次数超过限制
        if attempts and int(attempts) >= 10:
            return False, '验证码尝试次数过多，请稍后再试'

        # 验证码验证逻辑
        redis_key = f'verify_code:{email}'
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

    async def generate_reset_token(self, email: str, expires_in: int = 60) -> Tuple[bool, str]:
        """
        为密码重置生成令牌
        :param email: 目标邮箱
        :param expires_in: 过期时间，默认1小时
        :return: (是否成功, 消息或令牌)
        """
        # 生成随机令牌
        reset_token = secrets.token_urlsafe(32)

        # 构建重置链接
        reset_link = f'{settings.USER_FE_URL}/reset-password?token={reset_token}'
        # 发送重置邮件
        text = f"""
        您好，

        您请求了密码重置。请点击以下链接重置您的密码：

        {reset_link}

        此链接将在 1 小时后失效。
        如果您没有请求重置密码，请忽略此邮件。

        祝好，
        {self.logo_name} 团队
        """

        success, msg = self.email_manager.send_email(email, text, subject=f'{self.logo_name} 密码重置')

        if success:
            # 在Redis中存储重置令牌，使用特定前缀区分
            redis_key = f'reset_token:{reset_token}'
            # 存储邮箱，用于后续验证
            await set_cache(redis_key, email, expires_in * 60)
            return True, '重置链接已发送到您的邮箱'

        return False, msg

    async def verify_reset_token(self, token: str) -> Tuple[bool, str]:
        """
        验证重置令牌
        :param token: 重置令牌
        :return: (是否验证成功, 邮箱或错误消息)
        """
        redis_key = f'reset_token:{token}'
        email = await get_cache(redis_key)

        if not email:
            return False, '重置链接无效或已过期，请回到登录页重试'
        await delete_cache(redis_key)  # 删除令牌
        return True, email
