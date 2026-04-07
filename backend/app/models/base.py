import asyncio
import uuid
from datetime import datetime
from tortoise import fields, models
from decimal import Decimal
from core.config import settings


# 基础模型，自带主键id
class BaseModel(models.Model):
    id = fields.BigIntField(pk=True, index=True)

    # 模型实例转字典，m2m：是否包含多对多字段
    async def to_dict(self, m2m: bool = False, exclude_fields: list[str] | None = None):
        if exclude_fields is None:
            exclude_fields = []

        d = {}
        for field in self._meta.db_fields:
            if field not in exclude_fields:
                value = getattr(self, field)
                if isinstance(value, datetime):
                    value = value.strftime(settings.DATETIME_FORMAT)
                elif isinstance(value, Decimal):  # 处理 Decimal 类型
                    value = float(value)
                elif hasattr(value, 'hex'):  # 处理 UUID 类型
                    value = str(value)  # value.hex 没有破折号
                d[field] = value

        if m2m:
            tasks = [
                self.__fetch_m2m_field(field, exclude_fields)
                for field in self._meta.m2m_fields
                if field not in exclude_fields
            ]
            results = await asyncio.gather(*tasks)
            for field, values in results:
                d[field] = values

        return d

    async def __fetch_m2m_field(self, field, exclude_fields):
        values = await getattr(self, field).all().values()
        formatted_values = []

        for value in values:
            formatted_value = {}
            for k, v in value.items():
                if k not in exclude_fields:
                    if isinstance(v, datetime):
                        formatted_value[k] = v.strftime(settings.DATETIME_FORMAT)
                    else:
                        formatted_value[k] = v
            formatted_values.append(formatted_value)

        return field, formatted_values

    class Meta:
        abstract = True


# 提供uuid字段，适合需要全局唯一标识的模型
class UUIDModel:
    uuid = fields.UUIDField(unique=True, pk=False, index=True, default=uuid.uuid4)


# 自动记录创建和更新时间
class TimestampMixin:
    # 这里写入的是 utc 时间，但读取时 toroise 会自动将时间转换为config中设置的时区时间
    # auto_now_add仅在第一次创建时自动设置为当前时间
    create_at = fields.DatetimeField(auto_now_add=True, index=True)
    # auto_now每次更新时自动设置为当前时间
    update_at = fields.DatetimeField(auto_now=True, index=True)
