import jwt
from passlib.context import CryptContext
from schemas.login import JWTPayload
from .config import settings

pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')


# * 在这里表示强制使用关键字参数（Keyword-Only Arguments）。这意味着调用这个函数时，必须明确指定参数名。
def create_token(*, data: JWTPayload):
    payload = data.model_dump().copy()
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
