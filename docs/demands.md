# AI 记账应用需求文档

## 1. 项目概述

### 1.1 项目背景

本项目是一款面向个人用户的 AI 记账应用，帮助用户记录日常收入和支出，并通过报表功能分析消费习惯。用户可通过邮箱注册登录，数据存储在云端，支持多设备同步。

### 1.2 项目目标

- 提供简洁高效的收支记录功能
- 支持多账本管理
- 支持多类别管理（系统预设 + 用户自定义）
- 生成月度、年度支出报表
- 保证用户数据安全与隐私

### 1.3 目标用户

- 个人用户：希望管理日常财务
- 需求：简单易用、支持多账本分类管理

---

## 2. 功能需求

### 2.1 用户模块

#### 2.1.1 邮箱注册

| 需求编号 | FR-USER-001 |
|----------|-------------|
| 需求描述 | 用户通过邮箱注册账号 |
| 业务流程 | 1. 用户输入邮箱地址<br>2. 系统发送验证码到邮箱<br>3. 用户输入验证码<br>4. 系统验证通过后创建账号 |
| 前置条件 | 用户尚未注册 |
| 后置条件 | 用户注册成功，自动登录 |

#### 2.1.2 邮箱登录

| 需求编号 | FR-USER-002 |
|----------|-------------|
| 需求描述 | 用户通过邮箱和密码登录 |
| 业务流程 | 1. 用户输入邮箱和密码<br>2. 系统验证 credentials<br>3. 验证通过后返回 JWT Token |
| 前置条件 | 用户已完成注册 |
| 后置条件 | 登录成功，获取用户 Token |

### 2.2 账本模块

#### 2.2.1 创建账本

| 需求编号 | FR-LEDGER-001 |
|----------|---------------|
| 需求描述 | 用户创建一个新账本 |
| 业务流程 | 1. 选择创建方式（空白账本/模板创建）<br>2. 选择账本模板或输入账本名称<br>3. 可选填写账本描述<br>4. 保存 |
| 创建方式 | 空白账本、模板复制 |
| 必填字段 | 账本名称 |
| 选填字段 | 描述 |

**账本模板：**

| 模板名称 | 预设类别 |
|----------|----------|
| 日常账本 | 工资奖金、餐饮、交通、购物、娱乐、其他 |
| 旅行账本 | 机票、住宿、餐饮、交通、门票、购物、其他 |
| 医疗账本 | 门诊、住院、药品、检查、其他 |
| 家庭账本 | 工资、餐饮、教育、医疗、房租、其他 |

#### 2.2.2 查看账本列表

| 需求编号 | FR-LEDGER-002 |
|----------|---------------|
| 需求描述 | 用户查看自己的账本列表 |
| 业务流程 | 1. 进入账本列表页<br>2. 展示用户创建的所有账本 |
| 显示内容 | 账本名称、描述、创建时间、交易数量 |

#### 2.2.3 编辑账本

| 需求编号 | FR-LEDGER-003 |
|----------|---------------|
| 需求描述 | 用户修改账本信息 |
| 业务流程 | 1. 点击账本设置<br>2. 修改名称/描述<br>3. 保存 |

#### 2.2.4 删除账本

| 需求编号 | FR-LEDGER-004 |
|----------|---------------|
| 需求描述 | 用户删除账本 |
| 业务流程 | 1. 点击删除<br>2. 确认删除<br>3. 账本及关联数据一并删除 |

#### 2.2.5 账本切换

| 需求编号 | FR-LEDGER-005 |
|----------|---------------|
| 需求描述 | 用户在多个账本之间切换 |
| 业务流程 | 1. 点击账本切换器<br>2. 选择目标账本<br>3. 页面刷新为新账本数据 |

### 2.3 交易记录模块

#### 2.3.1 记录收入

| 需求编号 | FR-TRANS-001 |
|----------|-------------|
| 需求描述 | 用户记录一笔收入 |
| 业务流程 | 1. 选择账本<br>2. 选择「收入」类型<br>3. 输入金额<br>4. 选择类别<br>5. 可选填写备注<br>6. 选择交易日期（默认当天）<br>7. 提交保存 |
| 必填字段 | 账本、金额、类别、日期 |
| 选填字段 | 备注 |

#### 2.3.2 记录支出

| 需求编号 | FR-TRANS-002 |
|----------|-------------|
| 需求描述 | 用户记录一笔支出 |
| 业务流程 | 1. 选择账本<br>2. 选择「支出」类型<br>3. 输入金额<br>4. 选择类别<br>5. 可选填写备注<br>6. 选择交易日期（默认当天）<br>7. 提交保存 |
| 必填字段 | 账本、金额、类别、日期 |
| 选填字段 | 备注 |

#### 2.3.3 查看交易列表

| 需求编号 | FR-TRANS-003 |
|----------|-------------|
| 需求描述 | 用户查看指定账本的交易记录列表 |
| 业务流程 | 1. 进入交易列表页<br>2. 按日期倒序展示<br>3. 支持按月份筛选 |
| 显示内容 | 日期、类型、金额、类别、备注、记账人 |
| 分页 | 每页 20 条，支持翻页 |

#### 2.3.4 编辑交易记录

| 需求编号 | FR-TRANS-004 |
|----------|-------------|
| 需求描述 | 用户修改已保存的交易记录 |
| 业务流程 | 1. 点击记录进入编辑页面<br>2. 修改任意字段<br>3. 保存更新 |

#### 2.3.5 删除交易记录

| 需求编号 | FR-TRANS-005 |
|----------|-------------|
| 需求描述 | 用户删除某笔交易记录 |
| 业务流程 | 1. 点击删除按钮<br>2. 确认删除<br>3. 记录从列表中移除 |
| 确认机制 | 需要二次确认 |

### 2.4 类别管理模块

#### 2.4.1 系统预设类别

| 需求编号 | FR-CATE-001 |
|----------|-------------|
| 需求描述 | 系统预设常用的收入/支出类别 |

**收入类别：**

| 类别名称 | 图标 |
|----------|------|
| 工资 | wallet |
| 奖金 | gift |
| 投资收益 | trending-up |
| 兼职 | briefcase |
| 红包 | gift |
| 退款 | rotate-ccw |
| 其他收入 | more |

**支出类别：**

| 类别名称 | 图标 |
|----------|------|
| 餐饮 | restaurant |
| 交通 | car |
| 购物 | shopping |
| 娱乐 | game |
| 房租 | home |
| 医疗 | hospital |
| 教育 | book |
| 通讯 | phone |
| 服装 | shirt |
| 日用品 | basket |
| 社交 | users |
| 旅行 | plane |
| 宠物 | paw |
| 其他支出 | more |

#### 2.4.2 用户自定义类别

| 需求编号 | FR-CATE-002 |
|----------|-------------|
| 需求描述 | 用户创建自定义类别 |
| 业务流程 | 1. 选择类别类型（收入/支出）<br>2. 输入类别名称<br>3. 可选选择图标<br>4. 保存 |
| 限制 | 同一用户下类别名称不能重复 |

### 2.5 报表模块

#### 2.5.1 月度支出报表

| 需求编号 | FR-REPORT-001 |
|----------|-------------|
| 需求描述 | 查看指定账本指定月份的支出报表 |
| 输入参数 | 账本ID（ledger_id）、年份（year）、月份（month） |
| 返回数据 | - 月度总收入<br>- 月度总支出<br>- 结余（收入-支出）<br>- 按类别汇总的支出（含占比）<br>- 每日收支趋势 |
| 默认值 | 默认显示当前账本、当前月份 |

#### 2.5.2 年度支出报表

| 需求编号 | FR-REPORT-002 |
|----------|-------------|
| 需求描述 | 查看指定账本指定年份的年度报表 |
| 输入参数 | 账本ID（ledger_id）、年份（year） |
| 返回数据 | - 年度总收入<br>- 年度总支出<br>- 结余<br>- 每月收支汇总 |
| 默认值 | 默认显示当前账本、当前年份 |

#### 2.5.3 月份/年份选择

| 需求编号 | FR-REPORT-003 |
|----------|-------------|
| 需求描述 | 报表页面支持选择不同月份/年份 |
| 交互方式 | 下拉选择器 |
| 范围 | 可选择过去 5 年内的任意月份 |

---

## 3. 数据模型

### 3.1 交易类型枚举

```python
class TransactionType:
    INCOME = 1  # 收入
    EXPENSE = 2  # 支出
```

### 3.2 用户表 (User)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Int | 主键 |
| user_id | Char(12) | 用户唯一标识 |
| user_name | Char(20) | 用户名称 |
| email | Char(128) | 邮箱（唯一） |
| password | Char(128) | 密码（bcrypt 哈希存储） |
| avatar | Char(255) | 头像 |
| role_id | Int | 角色 ID |
| is_active | Boolean | 是否启用 |
| is_del | Boolean | 是否注销 |
| created_at | Datetime | 创建时间 |
| updated_at | Datetime | 更新时间 |

### 3.4 账本表 (Ledger)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Int | 主键 |
| user_id | Char(12) | 所属用户ID |
| name | Char(50) | 账本名称 |
| description | Char(200) | 账本描述 |
| created_at | Datetime | 创建时间 |
| updated_at | Datetime | 更新时间 |

### 3.5 类别表 (Category)

> **设计说明**：类别是用户级资源，不再绑定账本。系统预设类别（user_id=null）的 is_system=true，所有用户可见；用户自定义类别（user_id=当前用户）仅该用户可见。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Int | 主键 |
| user_id | Char(12) | 所属用户ID，null 表示系统预设 |
| name | Char(50) | 类别名称 |
| type | Int | 1=收入, 2=支出 |
| icon | Char(50) | 图标名称 |
| is_system | Boolean | 是否系统预设 |
| order | Int | 排序，数值越小越靠前 |
| created_at | Datetime | 创建时间 |
| updated_at | Datetime | 更新时间 |

### 3.6 交易记录表 (Transaction)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Int | 主键 |
| ledger_id | Int | 账本ID |
| tx_type | Int | 1=收入, 2=支出 |
| amount | Decimal(12,2) | 金额 |
| category_id | Int | 类别 ID |
| remark | Char(500) | 备注 |
| tx_date | Date | 交易日期（索引） |
| created_at | Datetime | 创建时间 |
| updated_at | Datetime | 更新时间 |

---

## 4. API 设计

### 4.1 认证模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/email_code | 发送邮箱验证码 |
| POST | /api/v1/auth/email_register | 邮箱注册 |
| POST | /api/v1/auth/email_login | 邮箱登录 |

### 4.2 账本模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/ledger | 获取账本列表 |
| POST | /api/v1/ledger | 创建账本 |
| PUT | /api/v1/ledger/{id} | 更新账本信息 |
| DELETE | /api/v1/ledger/{id} | 删除账本 |

### 4.3 类别模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/category?ledger_id={id} | 获取指定账本的类别列表 |
| POST | /api/v1/category | 创建自定义类别 |

### 4.4 交易模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/transaction?ledger_id={id} | 获取指定账本的交易列表 |
| POST | /api/v1/transaction | 创建交易记录 |
| PUT | /api/v1/transaction/{id} | 更新交易记录 |
| DELETE | /api/v1/transaction/{id} | 删除交易记录 |

### 4.5 报表模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/report/monthly?ledger_id={id}&year={year}&month={month} | 月度报表 |
| GET | /api/v1/report/yearly?ledger_id={id}&year={year} | 年度报表 |

---

## 5. API 返回结构

### 5.1 通用响应格式

**成功响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

**失败响应：**
```json
{
  "code": 400,
  "msg": "错误信息"
}
```

### 5.2 认证模块

#### 5.2.1 发送邮箱验证码

**请求：**
```json
POST /api/v1/auth/email_code
{
  "email": "user@example.com"
}
```

**响应：**
```json
{
  "code": 200,
  "msg": "验证码已发送"
}
```

#### 5.2.2 邮箱注册

**请求：**
```json
POST /api/v1/auth/email_register
{
  "email": "user@example.com",
  "code": "123456",
  "password": "password123",
  "remember": true
}
```

**响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "user_id": "ABC12345"
  }
}
```

#### 5.2.3 邮箱登录

**请求：**
```json
POST /api/v1/auth/email_login
{
  "email": "user@example.com",
  "password": "password123",
  "remember": false
}
```

**响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "user_id": "ABC12345"
  }
}
```

### 5.3 账本模块

#### 5.3.1 获取账本列表

**请求：**
```json
GET /api/v1/ledger
```

**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "日常账本",
      "description": "记录日常生活开支",
      "user_id": "ABC12345",
      "transaction_count": 100,
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "家庭账本",
      "description": "家庭共同开支",
      "user_id": "ABC12345",
      "transaction_count": 50,
      "created_at": "2025-02-01T00:00:00Z"
    }
  ]
}
```

#### 5.3.2 创建账本

**请求：**
```json
POST /api/v1/ledger
{
  "name": "旅行账本",
  "description": "记录旅行开支"
}
```

**响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 3,
    "name": "旅行账本",
    "description": "记录旅行开支",
    "user_id": "ABC12345",
    "created_at": "2025-04-20T00:00:00Z"
  }
}
```

### 5.4 类别模块

#### 5.4.1 获取类别列表

**请求：**
```json
GET /api/v1/category?ledger_id=1
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "income": [
      { "id": 1, "name": "工资奖金", "icon": "salary", "is_system": true },
      { "id": 2, "name": "投资收益", "icon": "invest", "is_system": true },
      { "id": 3, "name": "兼职外快", "icon": "part-time", "is_system": true },
      { "id": 4, "name": "礼金", "icon": "gift", "is_system": true },
      { "id": 5, "name": "其他", "icon": "other", "is_system": true }
    ],
    "expense": [
      { "id": 6, "name": "餐饮", "icon": "food", "is_system": true },
      { "id": 7, "name": "交通", "icon": "traffic", "is_system": true },
      { "id": 8, "name": "购物", "icon": "shopping", "is_system": true },
      { "id": 9, "name": "医疗", "icon": "medical", "is_system": true },
      { "id": 10, "name": "教育", "icon": "education", "is_system": true },
      { "id": 11, "name": "房租", "icon": "rent", "is_system": true },
      { "id": 12, "name": "通讯", "icon": "communication", "is_system": true },
      { "id": 13, "name": "娱乐", "icon": "entertainment", "is_system": true },
      { "id": 14, "name": "其他", "icon": "other", "is_system": true }
    ]
  }
}
```

#### 5.4.2 创建自定义类别

**请求：**
```json
POST /api/v1/category
{
  "ledger_id": 1,
  "name": "奶茶",
  "type": 2,
  "icon": "饮品"
}
```

**响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 15,
    "ledger_id": 1,
    "name": "奶茶",
    "type": 2,
    "icon": "饮品",
    "is_system": false
  }
}
```

### 5.5 交易模块

#### 5.5.1 获取交易列表

**请求：**
```json
GET /api/v1/transaction?ledger_id=1&page=1&page_size=20&month=4&year=2025
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": 1,
        "type": 2,
        "amount": 150.00,
        "category": { "id": 6, "name": "餐饮", "icon": "food" },
        "remark": "午餐",
        "date": "2025-04-15",
        "user_id": "ABC12345",
        "user_name": "张三",
        "created_at": "2025-04-15T12:00:00Z"
      },
      {
        "id": 2,
        "type": 1,
        "amount": 10000.00,
        "category": { "id": 1, "name": "工资奖金", "icon": "salary" },
        "remark": "月薪",
        "date": "2025-04-10",
        "user_id": "ABC12345",
        "user_name": "张三",
        "created_at": "2025-04-10T09:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

#### 5.5.2 创建交易记录

**请求：**
```json
POST /api/v1/transaction
{
  "ledger_id": 1,
  "type": 2,
  "amount": 150.00,
  "category_id": 6,
  "remark": "午餐",
  "date": "2025-04-15"
}
```

**响应：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1
  }
}
```

#### 5.5.3 更新交易记录

**请求：**
```json
PUT /api/v1/transaction/1
{
  "amount": 200.00,
  "remark": "午餐+晚餐"
}
```

**响应：**
```json
{
  "code": 200,
  "msg": "更新成功"
}
```

#### 5.5.4 删除交易记录

**请求：**
```json
DELETE /api/v1/transaction/1
```

**响应：**
```json
{
  "code": 200,
  "msg": "删除成功"
}
```

### 5.6 报表模块

#### 5.6.1 月度报表

**请求：**
```json
GET /api/v1/report/monthly?ledger_id=1&year=2025&month=4
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "ledger_id": 1,
    "ledger_name": "日常账本",
    "year": 2025,
    "month": 4,
    "total_income": 15000.00,
    "total_expense": 5000.00,
    "balance": 10000.00,
    "expense_by_category": [
      { "category": "餐饮", "amount": 1200.00, "percentage": 24 },
      { "category": "交通", "amount": 800.00, "percentage": 16 },
      { "category": "购物", "amount": 1000.00, "percentage": 20 },
      { "category": "房租", "amount": 2000.00, "percentage": 40 }
    ],
    "daily_data": [
      { "date": "2025-04-01", "income": 0, "expense": 150 },
      { "date": "2025-04-02", "income": 0, "expense": 200 },
      { "date": "2025-04-03", "income": 0, "expense": 80 },
      { "date": "2025-04-10", "income": 10000, "expense": 0 },
      { "date": "2025-04-15", "income": 0, "expense": 1200 }
    ]
  }
}
```

#### 5.6.2 年度报表

**请求：**
```json
GET /api/v1/report/yearly?ledger_id=1&year=2025
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "ledger_id": 1,
    "ledger_name": "日常账本",
    "year": 2025,
    "total_income": 180000.00,
    "total_expense": 60000.00,
    "balance": 120000.00,
    "monthly_data": [
      { "month": 1, "income": 15000, "expense": 5000 },
      { "month": 2, "income": 15000, "expense": 4500 },
      { "month": 3, "income": 15000, "expense": 6000 },
      { "month": 4, "income": 15000, "expense": 5000 }
    ]
  }
}
```

---

## 6. 界面设计要求

### 6.1 页面结构

| 页面 | 路由 | 说明 |
|------|------|------|
| 首页/仪表盘 | / | 账本切换、快捷操作入口 |
| 账本管理 | /ledgers | 账本列表、创建 |
| 交易记录 | /transactions | 列表 + 添加 |
| 报表 | /reports | 月度/年度报表 |
| 我的 | /profile | 用户设置 |

### 6.2 交互要求

- 账本切换：顶部导航栏账本名称，点击展开账本列表
- 添加交易：点击底部 FAB 按钮，弹出表单（表单内选择账本）
- 报表切换：Tab 切换月度/年度，下拉选择时间
- 删除确认：模态框二次确认

---

## 7. 非功能需求

### 7.1 安全性

- 密码使用 bcrypt 哈希存储
- API 接口需要 JWT Token 认证
- 用户数据隔离（只能操作自己的账本）
- 用户数据隔离（只能操作自己的账本）

### 7.2 性能

- 列表查询响应时间 < 500ms
- 报表生成响应时间 < 1s

### 7.3 兼容性

- 支持 Chrome、Safari、Firefox 最新版本
- 移动端响应式适配

---

## 8. 验收标准

### 8.1 注册登录

- [ ] 可以通过邮箱接收验证码
- [ ] 验证码有效期 5 分钟
- [ ] 邮箱未注册时提示用户
- [ ] 登录后 Token 正确返回

### 8.2 账本管理

- [ ] 可以创建账本
- [ ] 可以查看账本列表
- [ ] 可以编辑账本信息
- [ ] 可以删除账本
- [ ] 可以切换不同账本
- [ ] 可以通过模板创建账本

### 8.3 交易记录

- [ ] 可以添加收入记录（选择账本）
- [ ] 可以添加支出记录（选择账本）
- [ ] 可以编辑已有记录
- [ ] 可以删除记录（需确认）
- [ ] 列表按日期倒序显示
- [ ] 显示记账人信息

### 8.4 类别管理

- [ ] 显示系统预设类别
- [ ] 可以创建自定义类别
- [ ] 自定义类别只在当前账本可见

### 8.5 报表

- [ ] 月度报表正确显示收支汇总
- [ ] 月度报表显示类别占比
- [ ] 年度报表显示每月汇总
- [ ] 可以切换不同月份/年份
- [ ] 可以切换不同账本查看报表

---

## 9. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2025-04-21 | 初始版本 |
| v1.1 | 2025-04-28 | 新增账本模块，支持模板创建 |
