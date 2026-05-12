from typing import Optional
from pydantic import BaseModel, Field


# ============ Ledger 账本 ============
class LedgerCreate(BaseModel):
    name: str = Field(..., max_length=50, description='账本名称', example='我的账本')
    description: Optional[str] = Field(default=None, max_length=200, description='账本描述', example='日常收支记录')
    icon: Optional[str] = Field(default=None, max_length=50, description='账本图标', example='wallet')
    is_default: Optional[bool] = Field(default=False, description='是否为默认账本')


class LedgerUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50, description='账本名称')
    description: Optional[str] = Field(default=None, max_length=200, description='账本描述')
    icon: Optional[str] = Field(default=None, max_length=50, description='账本图标')
    is_default: Optional[bool] = Field(default=None, description='是否为默认账本')


# ============ Category 类别 ============
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=50, description='类别名称', example='餐饮')
    tx_type: int = Field(..., description='类型: 1=收入, 2=支出')
    icon: Optional[str] = Field(default=None, max_length=50, description='图标', example='food')
    order: Optional[int] = Field(default=0, description='排序')


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50, description='类别名称')
    tx_type: Optional[int] = Field(default=None, description='类型')
    icon: Optional[str] = Field(default=None, max_length=50, description='图标')
    order: Optional[int] = Field(default=None, description='排序')
