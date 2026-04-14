import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate' // 引入 Pinia 状态持久化插件
import '@/styles/normalize.css'
import '@/styles/index.css'
import 'uno.css' // 引入 uno.css 样式库

import App from './App.vue'
import { createAuthGuard, router } from './router'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)

createAuthGuard(router)
app.use(router)

app.mount('#app')
