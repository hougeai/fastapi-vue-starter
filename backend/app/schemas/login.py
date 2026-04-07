from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class JWTOut(BaseModel):
    access_token: str
    user_id: str


class JWTPayload(BaseModel):
    user_id: str
    exp: datetime


# 手机号注册登录相关
class PhoneLogin(BaseModel):
    phone: str = Field(..., description='手机号', example='13800138000')
    password: str = Field(..., description='密码', example='123456')
    remember: Optional[bool] = False  # 是否记住登录状态


class PhoneRegister(BaseModel):
    phone: str = Field(None, description='手机号', example='13800138000')
    code: str = Field(None, description='验证码', example='123456')
    remember: Optional[bool] = False  # 是否记住登录状态
    inviter_id: str = Field(None, description='邀请人ID', example='123456')
