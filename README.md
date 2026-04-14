# FinAI - AI 智能记账

> FinAI 你的 AI 记账搭子 —— 支持语音/拍照极速记账、AI 智能分类与自动对账、多币种实时换算、个性化预算规划、长期财务记忆，打造您身边的全能 AI 财务管家！

## 项目简介

FinAI 是一个前后端分离的 AI 记账应用，前端基于 Vue 3 + Vite，后端基于 FastAPI + Tortoise ORM，集成 OpenAI 等 LLM 能力，提供智能化的记账与财务分析体验。

## 技术栈

### 前端

| 技术 | 说明 |
|------|------|
| **Vue 3** | 核心框架，Composition API |
| **Vite** | 构建工具，极速热重载 |
| **Arco Design Vue** | UI 组件库 |
| **UnoCSS** | 原子化 CSS 框架 |
| **Pinia** | 状态管理 |
| **Vue Router** | 路由管理 |
| **Axios** | HTTP 客户端 |
| **VueUse** | 实用工具集合 |

### 后端

| 技术 | 说明 |
|------|------|
| **FastAPI** | 高性能异步 Web 框架 |
| **Tortoise ORM** | 异步 ORM，支持 SQLite/PostgreSQL |
| **Pydantic** | 数据验证与序列化 |
| **Aerich** | 数据库迁移工具 |
| **Redis** | 缓存与验证码存储 |
| **JWT** | 用户认证 |
| **OpenAI** | LLM 智能能力集成 |

## 项目结构

```
fastapi-vue-starter/
├── frontend/                    # 前端项目
│   ├── public/                  # 静态资源（不经过构建）
│   │   ├── logo.svg             # 项目 Logo
│   │   └── favicon.ico          # 网站图标
│   ├── src/
│   │   ├── api/                 # HTTP API 接口封装
│   │   ├── assets/              # 静态资源（经过构建）
│   │   ├── components/          # 公共组件
│   │   ├── config/              # 项目配置（环境变量）
│   │   ├── layout/              # 布局组件
│   │   ├── router/              # 路由配置
│   │   ├── stores/              # 状态管理 (Pinia)
│   │   ├── styles/              # 全局样式
│   │   ├── utils/               # 工具函数
│   │   ├── views/               # 页面视图
│   │   ├── App.vue              # 根组件
│   │   └── main.js              # 应用入口
│   ├── .env                     # 前端环境变量
│   ├── vite.config.js           # Vite 构建配置
│   └── package.json             # 前端依赖
│
├── backend/                     # 后端项目
│   ├── app/
│   │   ├── api/v1/              # API 路由（版本化）
│   │   │   ├── base.py          # 认证/授权/登录接口
│   │   │   ├── user.py          # 用户管理接口
│   │   │   ├── roles.py         # 角色管理接口
│   │   │   ├── menus.py         # 菜单管理接口
│   │   │   ├── apis.py          # API 权限接口
│   │   │   └── auditlog.py      # 审计日志接口
│   │   ├── controllers/         # 业务逻辑层
│   │   │   ├── crud.py          # CRUD 泛型基类
│   │   │   └── user.py          # 用户业务逻辑
│   │   ├── core/                # 核心配置
│   │   │   ├── config.py        # 全局配置 (Settings)
│   │   │   ├── dependency.py    # 依赖注入（认证/权限）
│   │   │   ├── security.py      # JWT 工具
│   │   │   ├── redis_client.py  # Redis 连接
│   │   │   ├── llm.py           # LLM 调用封装
│   │   │   ├── voice.py         # 语音处理
│   │   │   └── minio.py         # 对象存储
│   │   ├── models/              # 数据模型 (Tortoise ORM)
│   │   ├── schemas/             # 请求/响应模型 (Pydantic)
│   │   ├── migrations/          # 数据库迁移文件
│   │   ├── data/                # 数据存储 (SQLite)
│   │   ├── main.py              # 应用入口
│   │   └── .env                 # 后端环境变量
│   ├── pyproject.toml           # 后端依赖
│   └── README.md                # 后端详细文档
│
└── README.md                    # 本文件
```

## 核心功能

- 🧾 **语音/拍照记账** — 语音说出或拍照上传账单，AI 自动识别金额与类目
- 💱 **多币种换算** — 支持全球主流币种实时汇率自动换算
- 🤖 **AI 智能分类** — 自动对账单进行分类整理，告别手动归类
- 📊 **预算规划** — 个性化预算建议与超支提醒
- 🔐 **权限管理** — RBAC 角色权限控制，支持多角色多层级

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.12
- pnpm（前端包管理）
- uv（后端包管理）

### 1. 克隆项目

```bash
git clone <repo-url>
cd fastapi-vue-starter
```

### 2. 启动后端

```bash
cd backend

# 安装依赖
uv sync

# 配置环境变量
cp app/.env.example app/.env
# 编辑 app/.env 填写数据库、Redis、OSS 等配置

# 启动服务
cd app
sh run.sh
```

后端启动后访问 API 文档：http://localhost:3002/docs

### 3. 启动前端

```bash
cd frontend

# 安装依赖
pnpm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 填写后端 API 地址等配置

# 启动开发服务器
pnpm dev
```

前端启动后访问：http://localhost:8078

### 4. 前端常用命令


```bash
pnpm dev        # 启动开发服务器
pnpm build      # 生产构建
pnpm preview    # 预览构建产物
pnpm lint       # ESLint 代码检查
pnpm format     # Prettier 格式化
```
