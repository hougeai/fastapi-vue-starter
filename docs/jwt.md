# JWT 双 Token 鉴权实现分析

## 一、后端实现

### 关键文件

| 文件 | 路径 | 作用 |
|------|------|------|
| **security.py** | `backend/app/core/security.py` | Token 生成、密码加密 |
| **dependency.py** | `backend/app/core/dependency.py` | 认证和权限依赖注入 |
| **base.py** | `backend/app/api/v1/base.py` | 登录、刷新 Token、用户信息 API |
| **config.py** | `backend/app/core/config.py` | JWT 配置参数 |
| **login.py** | `backend/app/schemas/login.py` | JWT 相关数据模型 |

---

### 1. JWT 配置 (`config.py`)

```python
# JWT 配置
JWT_SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'secret_key')
JWT_ALGORITHM: str = 'HS256'
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 默认 1 天
JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 365         # 默认 365 天
```

**关键点**：
- Access Token：短期令牌，默认 1 天过期
- Refresh Token：长期令牌，默认 365 天过期

---

### 2. Token 生成 (`security.py`)

```python
import jwt
from schemas.login import JWTPayload
from .config import settings

def create_token(*, data: JWTPayload):
    payload = data.model_dump().copy()
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
```

**核心逻辑**：使用 PyJWT 库，通过 HS256 算法签名生成 Token

---

### 3. 双 Token 生成 (`base.py` - generate_token_response)

```python
def generate_token_response(user, remember: bool = False):
    # 生成过期时间
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_expire = datetime.now(timezone.utc) + access_token_expires
    refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_expire = datetime.now(timezone.utc) + refresh_token_expires
    
    # 生成 access_token (短效)
    data = JWTOut(
        access_token=create_token(
            data=JWTPayload(user_id=user.user_id, exp=access_expire)
        ),
        user_id=user.user_id,
    )
    
    # 生成 refresh_token (长效)
    refresh_token = create_token(data=JWTPayload(user_id=user.user_id, exp=refresh_expire))
    
    # refresh_token 存储在 HttpOnly Cookie 中
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,       # 前端 JS 无法访问
        secure=False,
        max_age=max_age,
    )
    return response
```

**关键设计**：
- Access Token：包含 `user_id`，返回给前端存储在 localStorage
- Refresh Token：包含 `user_id`，存储在 HttpOnly Cookie（前端 JS 无法访问，防 XSS）

---

### 4. Token 验证与认证 (`dependency.py`)

```python
class AuthControl:
    @classmethod
    async def is_authed(cls, request: Request, token: str = Header(..., description='token验证')):
        try:
            decode_data = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
            user_id = decode_data.get('user_id')
            user = await User.filter(user_id=user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail='Authentication failed')
            CTX_USER_ID.set(user_id)
            request.state.user_id = user_id
            return user
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail='无效的Token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=419, detail='登录已过期')
```

**错误码**：
- 401：无效 Token 或用户不存在
- 419：Token 已过期

---

### 5. Token 刷新 API (`base.py` - refresh_token)

```python
@router.post('/refresh_token', summary='刷新token')
async def refresh_token(request: Request):
    # 从 cookie 中获取 refresh_token
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        return Fail(msg='refresh token不存在')
    
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload['user_id']
        user = await user_controller.get_by_user_id(user_id)
        
        # 生成新的 access_token
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_expire = datetime.now(timezone.utc) + access_token_expires
        
        data = JWTOut(
            access_token=create_token(data=JWTPayload(user_id=user.user_id, exp=access_expire)),
            user_id=user.user_id,
        )
        return Success(data=data.model_dump())
    except jwt.ExpiredSignatureError:
        return Fail(msg='refresh token已过期')
    except jwt.InvalidTokenError:
        return Fail(msg='无效的refresh token')
```

---

### 6. 登录 API (`base.py` - email_login)

```python
@router.post('/email_login', summary='邮箱登录')
async def email_login(request: EmailLogin):
    user = await user_controller.authenticate(request)  # 验证邮箱密码
    await user_controller.update_last_login(user.user_id)
    return generate_token_response(user, remember=request.remember)
```

---

## 二、前端实现

### 关键文件

| 文件 | 路径 | 作用 |
|------|------|------|
| **http.js** | `frontend/src/api/http.js` | Axios 请求/响应拦截器 |
| **token.js** | `frontend/src/utils/token.js` | Token 存取工具函数 |
| **LoginDialog.vue** | `frontend/src/components/LoginDialog.vue` | 登录对话框组件 |
| **user.js (store)** | `frontend/src/stores/user.js` | 用户状态管理 |
| **router/index.js** | `frontend/src/router/index.js` | 路由守卫 |

---

### 1. Token 存储工具 (`token.js`)

```javascript
export function getToken() {
  return localStorage.getItem('access_token')
}

export function setToken(token) {
  localStorage.setItem('access_token', token)
}

export function removeToken() {
  window.localStorage.removeItem('access_token')
}
```

**设计**：Access Token 存储在 localStorage，Refresh Token 存在后端 Cookie 中

---

### 2. 请求拦截器 (`http.js`)

```javascript
// 请求成功拦截器
function reqResolve(config) {
  if (config.noNeedToken) {
    return config
  }
  const token = getToken()
  if (token) {
    config.headers.token = config.headers.token || token
  }
  return config
}
```

**逻辑**：自动从 localStorage 读取 access_token 添加到请求 Header

---

### 3. 响应拦截器 - Token 自动刷新 (`http.js`)

```javascript
service.interceptors.response.use(resResolve, async function (error) {
  // 处理 419 登录过期
  if (data?.code === 419) {
    try {
      const res = await service.post('/base/refresh_token')
      setToken(res.data.access_token)  // 更新 localStorage 中的 token
      config.headers.token = res.data.access_token
      // 重试之前失败的请求
      return service(config)
    } catch (error) {
      // refresh token 也失败了，执行登出
      const userStore = useUserStore()
      userStore.logout()
      return Promise.reject(error)
    }
  }
  // 处理 401 未授权
  if (data?.code === 401) {
    const userStore = useUserStore()
    userStore.logout()
    return Promise.reject(error)
  }
})
```

**自动刷新流程**：
1. 收到 419 状态码（access token 过期）
2. 调用 `/base/refresh_token` 刷新
3. 新 token 更新到 localStorage
4. 重试失败的请求
5. 若 refresh token 也过期，则登出

---

### 4. 登录流程 (`LoginDialog.vue`)

```javascript
const handleLoginSuccess = async res => {
  setToken(res.data.access_token)  // 登录成功立即设置 token
  const userInfoResult = await userStore.getUserInfo()
  if (!userInfoResult.success) {
    return
  }
  // 跳转到目标页面或首页
  router.push(query.redirect ? { path: query.redirect, query } : '/home')
}
```

---

### 5. 路由守卫 (`router/index.js`)

```javascript
const WHITE_LIST = ['/', '/404', '/reset-password']

export function createAuthGuard(router) {
  router.beforeEach(async to => {
    const token = getToken()
    
    if (isNullOrWhitespace(token)) {
      if (WHITE_LIST.includes(to.path)) return true
      // 重定向到登录页，记录原目标路径
      return { path: '/', query: { ...to.query, redirect: to.path } }
    }
    return true
  })
}
```

---

### 6. 用户状态管理 (`stores/user.js`)

```javascript
async logout() {
  removeToken()          // 清除 localStorage 中的 access_token
  this.$reset()           // 清除 persist 数据
  router.push('/')
}
```

---

## 三、整体鉴权流程

### 登录流程

```
用户输入邮箱密码
    ↓
POST /base/email_login
    ↓
后端验证邮箱密码
    ↓
生成 access_token (1天) + refresh_token (365天)
    ↓
access_token 返回前端 → localStorage
refresh_token 存入 Cookie (HttpOnly)
    ↓
前端保存 token，跳转首页
```

### 请求认证流程

```
前端发起请求
    ↓
请求拦截器：从 localStorage 读取 access_token 添加到 Header
    ↓
后端验证 access_token
    ↓
验证成功 → 处理请求 → 返回数据
验证失败(401) → 返回错误
验证过期(419) → 返回错误
```

### Token 自动刷新流程

```
请求失败，状态码 419 (access token 过期)
    ↓
调用 POST /base/refresh_token
    ↓
后端从 Cookie 读取 refresh_token 验证
    ↓
refresh_token 有效 → 生成新 access_token 返回
refresh_token 无效 → 返回错误
    ↓
前端更新 localStorage 中的 access_token
    ↓
重试原请求
```

### 登出流程

```
前端调用 logout()
    ↓
清除 localStorage 中的 access_token
    ↓
Cookie 中的 refresh_token 由后端过期处理
    ↓
跳转到登录页
```

---

## 四、总结

### 双 Token 设计优势

| 特性 | 说明 |
|------|------|
| **安全性** | Refresh Token 存储在 HttpOnly Cookie，防 XSS 攻击 |
| **用户体验** | Access Token 过期时静默刷新，用户无感知 |
| **灵活性** | Access Token 有效期短，泄露风险低 |
| **持久登录** | Refresh Token 有效期长，支持长期登录 |

### 关键设计点

#### 后端

- 使用 PyJWT 库生成和验证 Token
- Access Token 有效期短（默认 1 天）
- Refresh Token 有效期长（默认 365 天），存储在 HttpOnly Cookie

#### 前端

- Axios 拦截器自动处理 Token 注入
- 响应拦截器自动处理 419 错误并刷新 Token
- localStorage 存储 Access Token
- 路由守卫验证登录状态
