import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()  # 加载环境变量

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    VERSION: str = '1.0'
    APP_TITLE: str = 'ai-practice 后端服务接口'
    APP_DESCRIPTION: str = 'async-backend-service'
    # URL 配置
    ADMIN_FE_URL: str = os.getenv('ADMIN_FE_URL', '')
    USER_FE_URL: str = os.getenv('USER_FE_URL', '')
    BACK_END_PORT: int = os.getenv('BACK_END_PORT', 3002)
    # JWT 配置
    JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'secret_key')
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 默认1天
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 365  # 默认365天
    # Redis配置
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = os.getenv('REDIS_PORT', 6379)
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD', '')  # 如果有密码的话
    REDIS_POOL_SIZE: int = os.getenv('REDIS_POOL_SIZE', 10)  # 连接池大小
    # 对象存储oss配置
    OSS_ACCESS_KEY_ID: str = os.getenv('OSS_ACCESS_KEY_ID', '')
    OSS_ACCESS_KEY_SECRET: str = os.getenv('OSS_ACCESS_KEY_SECRET', '')
    OSS_ENDPOINT: str = os.getenv('OSS_ENDPOINT', '')
    OSS_BUCKET_NAME: str = os.getenv('OSS_BUCKET_NAME', '')
    OSS_BUCKET_URL: str = os.getenv('OSS_BUCKET_URL', '')
    OSS_REGION: str = os.getenv('OSS_REGION', '')
    OSS_SECURE: bool = str(os.getenv('OSS_SECURE', 'True')).lower() in ['true', '1', 'yes']
    # 外部API-KEY配置
    SF_KEY: str = os.getenv('SF_KEY', '')
    GLM_KEY: str = os.getenv('GLM_KEY', '')
    # 超级管理员配置
    SUPER_ADMIN_NAME: str = os.getenv('SUPER_ADMIN_NAME', '')
    SUPER_ADMIN_PHONE: str = os.getenv('SUPER_ADMIN_PHONE', '')
    SUPER_ADMIN_PASSWORD: str = os.getenv('SUPER_ADMIN_PASSWORD', '')
    # 数据库配置
    TORTOISE_ORM: dict = {
        'connections': {
            # SQLite configuration
            'sqlite': {
                'engine': 'tortoise.backends.sqlite',
                'credentials': {'file_path': f'{BASE_DIR}/data/db.sqlite3'},  # Path to SQLite database file
            },
            # PostgreSQL configuration
            # Install with: tortoise-orm[asyncpg]
            'postgres': {
                'engine': 'tortoise.backends.asyncpg',
                'credentials': {
                    'host': os.getenv('PG_HOST', 'localhost'),
                    'port': os.getenv('PG_PORT', 5432),
                    'user': os.getenv('PG_USER', 'root'),
                    'password': os.getenv('PG_PASSWORD', 'root'),
                    'database': os.getenv('PG_DATABASE', 'espbot'),
                },
            },
        },
        # 可以定义多个应用，每个应用可以有不同的配置，这里定义了一个名为"models"的应用，其中的models包括app/models和aerich/models两个模块
        'apps': {
            'models': {
                'models': ['models', 'aerich.models'],
                'default_connection': os.getenv('DB_TYPE', 'sqlite'),
            },
        },
        'use_tz': True,  # Whether to use timezone-aware datetimes
        'timezone': 'Asia/Shanghai',  # Timezone setting
    }
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'


settings = Settings()
