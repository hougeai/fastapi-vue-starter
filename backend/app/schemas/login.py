from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class JWTOut(BaseModel):
    access_token: str
    user_id: str


class JWTPayload(BaseModel):
    user_id: str
    exp: datetime


# 邮箱注册登录相关
class EmailLogin(BaseModel):
    email: str = Field(..., description='邮箱', example='user@example.com')
    password: str = Field(..., description='密码', example='123456')
    remember: Optional[bool] = False  # 是否记住登录状态


class VerifyCodeRequest(BaseModel):
    email: str = Field(..., description='邮箱', example='user@example.com')


class RegisterRequest(BaseModel):
    email: str = Field(..., description='邮箱', example='user@example.com')
    user_name: str = Field(None, description='用户名', example='新用户')
    password: str = Field(..., description='密码', example='123456')
    verification_code: str = Field(..., description='验证码', example='123456')
    inviter_id: Optional[str] = Field(None, description='邀请人ID', example='123456')


# 兼容旧接口（已废弃，保留以防其他地方引用）
class PhoneLogin(BaseModel):
    phone: str = Field(..., description='手机号', example='13800138000')
    password: str = Field(..., description='密码', example='123456')
    remember: Optional[bool] = False


class PhoneRegister(BaseModel):
    phone: str = Field(None, description='手机号', example='13800138000')
    code: str = Field(None, description='验证码', example='123456')
    remember: Optional[bool] = False
    inviter_id: str = Field(None, description='邀请人ID', example='123456')
