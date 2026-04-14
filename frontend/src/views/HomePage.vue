<script setup>
import { getConfig } from '@/config'

const cases = [
  {
    name: '实景-主播-手前景1',
    video: 'https://ks3-cn-beijing.ksyun.com/ksplayer/h265/mp4_resource/jinjie_265.mp4'
  },
  {
    name: '实景-主播-手前景2',
    video: 'https://ks3-cn-beijing.ksyun.com/ksplayer/h265/mp4_resource/jinjie_265.mp4'
  },
  {
    name: '第一人称-包包直播',
    video: 'https://ks3-cn-beijing.ksyun.com/ksplayer/h265/mp4_resource/jinjie_265.mp4'
  },
  {
    name: '第一人称-防水涂层直播',
    video: 'https://ks3-cn-beijing.ksyun.com/ksplayer/h265/mp4_resource/jinjie_265.mp4'
  },
  {
    name: '第一人称-珠宝直播',
    video: 'https://ks3-cn-beijing.ksyun.com/ksplayer/h265/mp4_resource/jinjie_265.mp4'
  }
]
</script>

<template>
  <div class="w-full bg-gray-100 min-h-screen">
    <!-- 头部标题 -->
    <header class="px-6 py-2 shadow-sm">
      <div class="max-w-7xl mx-auto flex items-end space-x-4">
        <h1 class="text-xl font-bold text-black">
          AI驱动的<span class="text-red-500">多语种交互式直播平台</span>
        </h1>
        <p class="text-sm text-gray-600">人人皆可轻松开启的高质量AI直播间</p>
      </div>
    </header>

    <!-- 主视觉横幅 -->
    <section class="relative h-60 md:h-80 bg-black rounded-2xl overflow-hidden mb-12 mx-6">
      <img src="@/assets/img/banner.webp" alt="AI Agent 应用" class="w-full h-full object-cover" />
      <div class="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
        <div class="text-center text-white px-6">
          <h2 class="text-3xl md:text-4xl font-bold mb-2">
            迈向未来的<span
              class="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500"
              >AI Agent</span
            >应用
          </h2>
          <p class="text-xl md:text-2xl font-semibold">企业级多语种AI交互式直播生产平台</p>
        </div>
      </div>
    </section>

    <!-- 三步流程 -->
    <section class="px-6 pb-12">
      <div class="max-w-7xl mx-auto text-center mb-10">
        <h2 class="text-2xl font-bold text-black">
          只需 <span class="text-red-500 text-3xl">3</span> 步，轻松直播
        </h2>
      </div>

      <div class="flex flex-col md:flex-row justify-center gap-8">
        <!-- 第一步 -->
        <div
          class="w-full max-w-xs p-6 bg-[var(--color-warning-light-1)] rounded-xl shadow-md transition-transform hover:scale-105 flex flex-col items-center text-center"
        >
          <h3 class="text-lg font-semibold mb-2">创建直播项目</h3>
          <p class="text-sm text-gray-600 mb-4">提供商品、服务或其他相关资料</p>
          <button
            class="px-4 py-2 bg-white border border-orange-400 text-orange-600 rounded-md hover:bg-orange-50 transition-colors"
            @click="$router.push('/dashboard/product')"
          >
            创建项目
          </button>
        </div>

        <!-- 箭头 -->
        <div class="hidden md:flex items-center justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M5 12h14M12 5l7 7-7 7"></path>
          </svg>
        </div>

        <!-- 第二步 -->
        <div
          class="w-full max-w-xs p-6 bg-[var(--color-warning-light-1)] rounded-xl shadow-md transition-transform hover:scale-105 flex flex-col items-center text-center"
        >
          <h3 class="text-lg font-semibold mb-2">生成虚拟主播</h3>
          <p class="text-sm text-gray-600 mb-4">AI智能生成主播人设、语音和话术</p>
          <button
            class="px-4 py-2 bg-white border border-orange-400 text-orange-600 rounded-md hover:bg-orange-50 transition-colors"
            @click="$router.push('/dashboard/host-agent')"
          >
            创建主播
          </button>
        </div>

        <!-- 箭头 -->
        <div class="hidden md:flex items-center justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M5 12h14M12 5l7 7-7 7"></path>
          </svg>
        </div>

        <!-- 第三步 -->
        <div
          class="w-full max-w-xs p-6 bg-[var(--color-warning-light-1)] rounded-xl shadow-md transition-transform hover:scale-105 flex flex-col items-center text-center"
        >
          <h3 class="text-lg font-semibold mb-2">一键快速开播</h3>
          <p class="text-sm text-gray-600 mb-4">云端算力无限拓展免部署快速开播</p>
          <button
            class="px-4 py-2 bg-white border border-orange-400 text-orange-600 rounded-md hover:bg-orange-50 transition-colors"
            @click="$router.push('/dashboard/live-room')"
          >
            创建直播间
          </button>
        </div>
      </div>
    </section>

    <!-- 行业案例展示 -->
    <section class="px-6 pb-12">
      <div class="max-w-7xl mx-auto mb-8 text-center">
        <h2 class="text-xl font-semibold text-black">
          来看看各行业的人如何使用{{ getConfig('projectName') }}
        </h2>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div
          v-for="(item, index) in cases"
          :key="index"
          class="rounded-lg shadow-md overflow-hidden"
        >
          <video
            :src="item.video"
            class="w-full h-80 object-cover rounded-lg"
            controls
            controlslist="nodownload"
            preload="metadata"
          ></video>
          <div class="p-2 bg-white">
            <p class="text-center font-bold">{{ item.name }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* 自定义样式补充 */
@media (max-width: 768px) {
  .flex-row {
    flex-direction: column;
  }
}
</style>
