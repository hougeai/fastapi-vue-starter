from tortoise import fields
from .base import BaseModel, TimestampMixin
from .enums import TransactionType


# 账本表
class Ledger(BaseModel, TimestampMixin):
    user_id = fields.CharField(max_length=12, description='所属用户ID', index=True)
    name = fields.CharField(max_length=50, description='账本名称', index=True)
    description = fields.CharField(max_length=200, null=True, description='账本描述')
    icon = fields.CharField(max_length=50, null=True, description='账本图标')
    is_default = fields.BooleanField(default=False, description='是否为默认账本')

    class Meta:
        table = 'ledger'


# 类别表（用户级）
# - user_id=null + is_system=true  : 系统预设，所有用户可见
# - user_id=<当前用户>              : 用户自定义，仅该用户可见
class Category(BaseModel, TimestampMixin):
    user_id = fields.CharField(max_length=12, null=True, description='所属用户ID，null表示系统预设', index=True)
    name = fields.CharField(max_length=50, description='类别名称', index=True)
    tx_type = fields.IntEnumField(TransactionType, description='类型: 1=收入, 2=支出', index=True)
    icon = fields.CharField(max_length=50, null=True, description='图标')
    is_system = fields.BooleanField(default=False, description='是否系统预设')
    order = fields.IntField(default=0, description='排序')

    class Meta:
        table = 'category'
