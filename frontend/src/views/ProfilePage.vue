<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(async () => {
  await userStore.getUserInfo()
})
</script>

<template>
  <div class="w-full p-6 bg-[var(--color-fill-0)] min-h-screen">
    <div class="text-center text-gray-400">
      我的 - 用户设置
    </div>
  </div>
</template>
