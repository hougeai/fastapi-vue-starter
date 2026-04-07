# AI-Practice Backend

基于 FastAPI + Tortoise ORM 的异步后端服务。

## 技术栈

| 技术 | 说明 |
|------|------|
| **FastAPI** | 高性能异步 Web 框架 |
| **Tortoise ORM** | 异步 ORM，支持 SQLite/PostgreSQL |
| **Pydantic** | 数据验证与序列化 |
| **Aerich** | 数据库迁移工具 |
| **Redis** | 缓存与验证码存储 |
| **JWT** | 用户认证 |

## 项目结构

```
backend/
├── app/
│   ├── api/                    # API 路由
│   │   ├── __init__.py         # 路由汇总
│   │   └── v1/
│   │       ├── __init__.py     # v1 路由入口
│   │       ├── apis.py         # API 管理接口
│   │       ├── auditlog.py     # 审计日志接口
│   │       ├── base.py         # 认证/授权/登录接口
│   │       ├── menus.py        # 菜单管理接口
│   │       ├── roles.py        # 角色管理接口
│   │       └── user.py         # 用户管理接口
│   ├── controllers/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── crud.py            # CRUD 基类（泛型实现）
│   │   └── user.py            # 用户相关业务逻辑
│   ├── core/                   # 核心配置
│   │   ├── config.py          # 全局配置（Settings）
│   │   ├── dependency.py       # 依赖注入（认证/权限）
│   │   ├── exceptions.py       # 全局异常处理
│   │   ├── init_app.py        # 应用初始化（DB/中间件/路由）
│   │   ├── middlewares.py     # 中间件（日志/审计）
│   │   ├── redis_client.py    # Redis 连接
│   │   ├── security.py        # JWT 工具
│   │   ├── verifycode.py      # 验证码管理
│   │   └── ...
│   ├── models/                 # Tortoise ORM 模型
│   │   ├── base.py            # 模型基类
│   │   ├── enums.py           # 枚举定义
│   │   └── user.py            # 用户/角色/API/菜单模型
│   ├── schemas/                # Pydantic 请求/响应模型
│   │   ├── base.py
│   │   ├── login.py           # 登录相关 schema
│   │   └── user.py            # 用户相关 schema
│   ├── main.py                # 应用入口
│   └── data/                  # 数据存储
│       └── db.sqlite3         # SQLite 数据库文件
├── pyproject.toml             # 项目依赖
└── .env                       # 环境变量
```

## 核心模块

### 1. 配置管理 (`core/config.py`)

使用 `pydantic-settings` 管理配置，支持环境变量：

- **数据库**: 支持 SQLite（默认）和 PostgreSQL
- **Redis**: 缓存和验证码存储
- **JWT**: Token 密钥和过期时间
- **OSS**: 对象存储配置

### 2. 数据模型 (`models/`)

```
User          # 用户表
Role          # 角色表
Api           # API 接口表（用于权限控制）
Menu          # 菜单表（管理后台用）
RoleMenu      # 角色-菜单关联表
RoleApi       # 角色-API 关联表
AuditLog      # 审计日志表
```

### 3. 认证授权 (`core/dependency.py`)

- `AuthControl`: JWT Token 验证
- `PermissionControl`: 基于角色的 API 权限控制

### 4. 业务逻辑 (`controllers/`)

使用泛型基类 `CRUDBase` 实现通用的增删改查：

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    - get()      # 获取单个
    - list()     # 分页列表
    - create()   # 创建
    - update()   # 更新
    - remove()   # 删除
```

### 5. API 版本

采用 `/api/v1/` 前缀的版本化路由设计。

## 快速开始

### 安装依赖

```bash
cd backend
uv sync
```

### 配置环境变量

```bash
cp app/.env.example app/.env
# 编辑 .env 填写必要的配置
```

### 启动服务

```bash
cd app
uv run python main.py
# 或使用脚本
bash run.sh
```

服务启动后访问: http://localhost:3002/docs

## 数据库

### 使用 SQLite（默认）

开箱即用，数据存储在 `app/data/db.sqlite3`

### 使用 PostgreSQL

```bash
# 安装异步驱动
uv add asyncpg

# 配置环境变量
DB_TYPE=postgres
PG_HOST=localhost
PG_PORT=5432
PG_USER=your_user
PG_PASSWORD=your_password
PG_DATABASE=your_db
```

### 数据库迁移

使用 Aerich 进行迁移管理：

```bash
# 初始化
aerich init -t app.settings.TORTOISE_ORM

# 生成迁移
aerich migrate

# 执行迁移
aerich upgrade
```

## API 文档

启动服务后访问 Swagger UI: `/docs`

### 主要接口

| 模块 | 说明 |
|------|------|
| `/api/v1/base/refresh_token` | 刷新 Token |
| `/api/v1/base/userinfo` | 获取用户信息 |
| `/api/v1/base/usermenu` | 获取用户菜单 |
| `/api/v1/base/userapi` | 获取用户 API 权限 |
| `/api/v1/base/phone_login` | 手机号登录 |
| `/api/v1/base/phone_register` | 手机号注册 |

## 权限系统

采用 RBAC（基于角色的访问控制）模型：

1. **角色** (Role): 超级管理员、管理员、免费会员、VIP会员
2. **API** (Api): 自动从路由扫描注册到数据库
3. **关联表**: RoleApi 将角色与 API 绑定

用户登录后通过 `/userapi` 接口获取其角色可访问的 API 列表，前端进行路由权限控制。

## 中间件

- **CORS**: 跨域资源共享
- **BackGroundTaskMiddleware**: 后台任务处理
- **HttpAuditLogMiddleware**: HTTP 请求审计日志
