<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getConfig } from '@/config'

// 导入图标
import IconRocket from '~icons/material-symbols/rocket-launch'
import IconInfoCircle from '~icons/material-symbols/info-outline'
import IconCamera from '~icons/material-symbols/photo-camera-outline'
import IconTranslate from '~icons/material-symbols/translate'
import IconAccountBalance from '~icons/material-symbols/account-balance-wallet-outline'
import IconArrowRight from '~icons/material-symbols/arrow-forward'
import IconAddCircle from '~icons/material-symbols/add-circle-outline'
import IconReceipt from '~icons/material-symbols/receipt-long'
import IconPlayCircle from '~icons/material-symbols/play-circle-outline'

const router = useRouter()
const route = useRoute()
const showLoginDialog = ref(false) // 控制登录弹窗显示

// 监听路由变化，如果存在redirect参数则显示登录对话框
watch(
  () => route.query,
  newQuery => {
    if (newQuery.redirect) {
      showLoginDialog.value = true
    }
  }
)

const handleLoginCancel = () => {
  // 如果 URL 中有 redirect 参数，取消时应该移除它
  if (route.query.redirect) {
    const newQuery = { ...route.query }
    delete newQuery.redirect
    router.replace({ query: newQuery })
  }
}
// 统计数据
const stats = ref([
  { label: '累计记账笔数', value: 0, target: 1000000, suffix: '+' },
  { label: '支持币种', value: 0, target: 50, suffix: '+' },
  { label: '用户节省时间', value: 0, target: 80000, suffix: '小时' }
])

// 功能特色
const features = [
  {
    icon: IconCamera,
    title: '语音/拍照记账',
    description: '语音说出或拍照上传账单，AI自动识别金额、类目，极速完成记账',
    color: 'rgb(var(--primary-6))'
  },
  {
    icon: IconTranslate,
    title: '多币种实时换算',
    description: '支持全球主流币种，实时汇率自动换算，跨国记账无忧',
    color: 'rgb(var(--success-6))'
  },
  {
    icon: IconAccountBalance,
    title: '智能预算规划',
    description: 'AI分析消费习惯，个性化预算建议与超支提醒，让财务更健康',
    color: 'rgb(var(--warning-6))'
  }
]

// 工具展示
const tools = [
  {
    name: '快速记一笔',
    description: '语音、拍照或手动输入，3秒完成一笔记账',
    icon: IconAddCircle,
    path: '/dashboard/product',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    name: '智能对账',
    description: 'AI自动分类与对账，告别手动整理的烦恼',
    icon: IconReceipt,
    path: '/dashboard/host-agent',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    name: '财务报告',
    description: '一键生成收支报告，消费趋势一目了然',
    icon: IconPlayCircle,
    path: '/dashboard/live-room',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  }
]

// 数字动画
const animateNumbers = () => {
  stats.value.forEach(stat => {
    let current = 0
    const increment = stat.target / 100
    const timer = setInterval(() => {
      current += increment
      if (current >= stat.target) {
        stat.value = stat.target
        clearInterval(timer)
      } else {
        stat.value = Math.floor(current)
      }
    }, 20)
  })
}

// 跳转到工具页面
const goToTool = path => {
  router.push(path)
}

// 滚动到功能特色区域
const scrollToFeatures = () => {
  const featuresSection = document.querySelector('.features-section')
  if (featuresSection) {
    featuresSection.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    })
  }
}

onMounted(() => {
  // 延迟执行数字动画
  setTimeout(() => {
    animateNumbers()
  }, 500)
})
</script>

<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-header">
          <div class="hero-logo-wrapper">
            <img src="/logo.svg" alt="Logo" class="hero-logo" />
          </div>
          <h1 class="hero-title">{{ getConfig('projectName') }}</h1>
          <div class="hero-logo-wrapper hero-logo-mirror">
            <img src="/logo.svg" alt="Logo" class="hero-logo" />
          </div>
        </div>
        <div class="hero-subtitle">
          <p>
            😎<span
              class="text-2xl font-bold bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent"
              >{{ getConfig('projectTitle') }}</span
            >😎
          </p>
          <span
            class="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-blue-500 bg-clip-text text-transparent"
            >{{ getConfig('projectDesc') }}</span
          >
        </div>
        <div class="hero-buttons">
          <a-button type="primary" size="large" @click="$router.push('/home')" class="cta-button">
            <template #icon>
              <IconRocket />
            </template>
            立即开始
          </a-button>
          <a-button size="large" class="learn-more-button" @click="scrollToFeatures">
            <template #icon>
              <IconInfoCircle />
            </template>
            了解更多
          </a-button>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="section-container">
        <div class="section-header">
          <h2 class="section-title">核心特色</h2>
          <p class="section-subtitle">为什么选择{{ getConfig('projectName') }}？</p>
        </div>
        <div class="features-grid">
          <div v-for="(feature, index) in features" :key="index" class="feature-card">
            <div class="feature-icon" :style="{ backgroundColor: feature.color }">
              <component :is="feature.icon" class="text-24px text-white" />
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Tools Showcase Section -->
    <section class="tools-section">
      <div class="section-container">
        <div class="section-header">
          <h2 class="section-title">三步轻松记账</h2>
          <p class="section-subtitle">只需3步，告别繁琐记账</p>
        </div>
        <div class="tools-scroll-container">
          <div class="tools-scroll-wrapper">
            <div
              v-for="(tool, index) in tools"
              :key="index"
              class="tool-card"
              @click="goToTool(tool.path)"
            >
              <div class="tool-header" :style="{ background: tool.color }">
                <component :is="tool.icon" class="text-32px text-white" />
              </div>
              <div class="tool-content">
                <h3 class="tool-title">{{ tool.name }}</h3>
                <p class="tool-description">{{ tool.description }}</p>
                <div class="tool-action">
                  <a-button type="text" size="small">
                    立即体验
                    <template #icon>
                      <IconArrowRight />
                    </template>
                  </a-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Statistics Section -->
    <section class="stats-section">
      <div class="section-container">
        <div class="stats-grid">
          <div v-for="(stat, index) in stats" :key="index" class="stat-card">
            <div class="stat-number">{{ stat.value.toLocaleString() }}{{ stat.suffix }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="section-container">
        <div class="cta-content">
          <h2 class="cta-title">准备好开启AI智能记账之旅了吗？</h2>
          <p class="cta-subtitle">加入我们，体验AI赋能的财务管理新方式</p>
          <a-button
            type="primary"
            size="large"
            @click="$router.push('/home')"
            class="cta-main-button"
          >
            <template #icon>
              <IconRocket />
            </template>
            立即开始
          </a-button>
        </div>
      </div>
    </section>

    <!-- 登录对话框 -->
    <LoginDialog v-model:visible="showLoginDialog" @cancel="handleLoginCancel" />
  </div>
</template>

<style scoped>
.landing-page {
  width: 100vw;
  min-height: 100vh;
  margin-left: calc(-50vw + 50%);
  background: linear-gradient(135deg, var(--color-bg-1) 0%, var(--color-bg-2) 100%);
}

/* Hero Section */
.hero-section {
  position: relative;
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow: hidden;
}

.hero-content {
  text-align: center;
  max-width: 800px;
  z-index: 2;
}

.hero-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.hero-logo-wrapper {
  animation: float 3s ease-in-out infinite;
  background: linear-gradient(
    135deg,
    rgba(var(--primary-6), 0.1) 0%,
    rgba(var(--purple-6), 0.1) 100%
  );
  border: 2px solid rgba(var(--primary-6), 0.2);
  border-radius: 50%;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(var(--primary-6), 0.15);
  transition: all 0.3s ease;
}

.hero-logo {
  width: 56px;
  height: 56px;
}

.hero-logo-mirror {
  transform: scaleX(-1);
}

.hero-title {
  font-size: 4rem;
  font-weight: 800;
  margin: 0;
  background: linear-gradient(135deg, rgb(var(--primary-6)) 0%, rgb(var(--purple-6)) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.5rem;
  color: var(--color-text-2);
  margin-bottom: 3rem;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-button {
  padding: 0 2rem;
  height: 48px;
  font-size: 1.1rem;
  border-radius: 24px;
  box-shadow: 0 4px 15px rgba(var(--primary-6), 0.3);
  transition: all 0.3s ease;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--primary-6), 0.4);
}

.learn-more-button {
  padding: 0 2rem;
  height: 48px;
  font-size: 1.1rem;
  border-radius: 24px;
  border: 2px solid rgb(var(--primary-6));
  color: rgb(var(--primary-6));
  transition: all 0.3s ease;
}

.learn-more-button:hover {
  background: rgb(var(--primary-6));
  color: white;
  transform: translateY(-2px);
}

/* Sections */
.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--color-text-1);
}

.section-subtitle {
  font-size: 1.2rem;
  color: var(--color-text-2);
}

.scroll-hint {
  font-size: 0.9rem;
  color: rgb(var(--primary-6));
  font-weight: 500;
  display: inline-block;
  margin-left: 0.5rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.7;
  }

  50% {
    opacity: 1;
  }
}

/* Features Section */
.features-section {
  padding: 4rem 0;
  background: var(--color-bg-1);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  border-radius: 16px;
  background: var(--color-bg-1);
  box-shadow: 0 4px 20px var(--color-shadow-light);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-text-1);
}

.feature-description {
  color: var(--color-text-2);
  line-height: 1.6;
}

/* Tools Section */
.tools-section {
  padding: 4rem 0;
  background: var(--color-bg-2);
}

.tools-scroll-container {
  position: relative;
  overflow: hidden;
  padding: 0 1rem;
}

.tools-scroll-wrapper {
  display: flex;
  gap: 2rem;
  overflow-x: auto;
  scroll-behavior: smooth;
  padding: 1rem 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(var(--primary-6), 0.3) transparent;
}

.tools-scroll-wrapper::-webkit-scrollbar {
  height: 8px;
}

.tools-scroll-wrapper::-webkit-scrollbar-track {
  background: var(--color-fill-2);
  border-radius: 4px;
}

.tools-scroll-wrapper::-webkit-scrollbar-thumb {
  background: var(--color-fill-4);
  border-radius: 4px;
  transition: background 0.3s ease;
}

.tools-scroll-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--color-fill-3);
}

.tool-card {
  flex: 0 0 350px;
  background: var(--color-bg-1);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px var(--color-shadow-light);
  transition: all 0.3s ease;
  cursor: pointer;
}

.tool-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px var(--color-shadow-medium);
}

.tool-header {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.tool-content {
  padding: 2rem;
  text-align: center;
}

.tool-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-text-1);
}

.tool-description {
  color: var(--color-text-2);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.tool-action {
  display: flex;
  justify-content: flex-end;
}

/* Statistics Section */
.stats-section {
  padding: 4rem 0;
  background: rgb(var(--primary-6));
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1.1rem;
  opacity: 0.9;
}

/* CTA Section */
.cta-section {
  padding: 6rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.cta-content {
  text-align: center;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.cta-subtitle {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta-main-button {
  padding: 0 3rem;
  height: 56px;
  font-size: 1.2rem;
  border-radius: 28px;
  background: white;
  color: rgb(var(--primary-6));
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.cta-main-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
}

/* Animations */
@keyframes float {
  0%,
  100% {
    transform: translateY(0px);
  }

  50% {
    transform: translateY(-20px);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-header {
    flex-direction: column;
    gap: 1rem;
  }

  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }

  .cta-button,
  .learn-more-button {
    width: 100%;
    max-width: 300px;
  }

  .tool-card {
    flex: 0 0 300px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 1rem;
  }

  .section-container {
    padding: 0 1rem;
  }

  .hero-title {
    font-size: 2rem;
  }

  .cta-title {
    font-size: 1.8rem;
  }
}
</style>
