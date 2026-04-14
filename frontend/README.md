# FinAI - AI智能记账前端

基于 Vue 3 和 Vite 构建的 AI 记账应用前端，支持语音/拍照极速记账、AI 智能分类与自动对账、多币种实时换算、个性化预算规划。

## 技术栈

- **核心框架**: [Vue 3](https://v3.vuejs.org/) Composition API
- **构建工具**: [Vite](https://vite.dev/)
- **语言**: JavaScript (ES6+)
- **UI框架**: [Arco Design Vue](https://arco.design/vue/docs/start)
- **CSS框架**: [UnoCSS](https://unocss.dev/) - 原子化 CSS
- **状态管理**: [Pinia](https://pinia.vuejs.org/)
- **路由管理**: [Vue Router](https://router.vuejs.org/)
- **HTTP客户端**: [Axios](https://axios-http.com/)
- **开发工具**: [VueUse](https://vueuse.org/) - 实用工具集合

## 项目特色

- 🧾 语音/拍照极速记账，AI 自动识别金额与类目
- 💱 多币种实时汇率换算，跨国记账无忧
- 🤖 AI 智能分类与自动对账，告别手动整理
- 📊 个性化预算规划与消费趋势分析
- 🚀 基于 Vite 构建，热重载速度快
- 🎨 使用 UnoCSS 原子化 CSS，样式编写更高效
- 📦 自动导入组件和 API，减少样板代码

## 项目结构

```
frontend/
├── public/                  # 静态资源（不经过构建）
│   ├── favicon.ico          # 网站图标
│   ├── logo.svg             # 项目 Logo
│   └── resource/            # 其他公共资源
├── src/
│   ├── api/                 # HTTP API 接口封装
│   │   ├── http.js          # Axios 实例与拦截器
│   │   └── index.js         # API 接口定义
│   ├── assets/              # 静态资源（经过构建）
│   │   └── img/             # 图片资源
│   ├── components/          # 公共组件
│   │   ├── LoginDialog.vue  # 登录对话框
│   │   └── TypeWriter.vue   # 打字机效果组件
│   ├── config/              # 项目配置
│   │   └── index.js         # 环境变量与全局配置
│   ├── layout/              # 布局组件
│   │   ├── DefaultLayout.vue    # 默认布局（导航栏+内容+页脚）
│   │   ├── SidebarLayout.vue    # 侧边栏布局
│   │   └── components/          # 布局子组件
│   │       ├── Logo.vue     # Logo 与页面标题
│   │       ├── NavBar.vue   # 顶部导航栏
│   │       └── ...          # 其他导航组件
│   ├── router/              # 路由配置
│   │   ├── index.js         # 路由入口
│   │   ├── defaultRouter.js # 默认路由
│   │   └── menuRouter.js    # 菜单路由
│   ├── stores/              # 状态管理 (Pinia)
│   │   ├── finance.js       # 记账数据
│   │   ├── user.js          # 用户信息
│   │   ├── notification.js  # 通知消息
│   │   └── ...              # 其他 Store
│   ├── styles/              # 全局样式
│   │   ├── index.css        # 样式入口
│   │   └── normalize.css    # 样式重置
│   ├── utils/               # 工具函数
│   │   ├── common.js        # 通用工具
│   │   ├── is.js            # 类型判断
│   │   └── token.js         # Token 管理
│   ├── views/               # 页面视图
│   │   ├── LandingPage.vue  # 落地页
│   │   ├── HomePage.vue     # 首页
│   │   ├── NotFoundPage.vue # 404 页面
│   │   ├── dashboard/       # 仪表盘页面
│   │   └── user-center/     # 用户中心页面
│   ├── App.vue              # 根组件
│   └── main.js              # 应用入口
├── .env                     # 环境变量
├── .env.example             # 环境变量示例
├── eslint.config.js         # ESLint 配置
├── index.html               # HTML 入口
├── jsconfig.json            # JS 项目配置
├── package.json             # 项目依赖与脚本
├── pnpm-lock.yaml           # 依赖锁定文件
├── vite.config.js           # Vite 构建配置
└── README.md                # 项目说明
```

## 代码检查和格式化

项目使用 ESLint 和 Prettier 进行代码检查和格式化。你可以使用以下命令来检查代码和格式化代码：

```
pnpm run lint # 检查代码
pnpm run format # 格式化代码
```
