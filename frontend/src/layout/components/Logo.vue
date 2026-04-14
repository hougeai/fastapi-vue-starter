<script setup>
import { getConfig } from '@/config'
const route = useRoute()
const title = useTitle() // 来自VueUse

watchEffect(() => {
  title.value = getConfig('projectName') + '-' + route.meta.title || getConfig('projectName')
})
</script>
<template>
  <div
    class="pr-4 h-full flex items-center text-16px font-700 text-shadow-sm cursor-pointer"
    @click="$router.push('/')"
  >
    <div
      class="w-36px h-36px rounded-[50%] flex justify-center items-center mr-2 cursor-pointer logo-icon"
      hover="bg-[var(--color-fill-1)]"
    >
      <img src="/logo.svg" alt="Logo" class="w-20px h-20px" />
    </div>
    <div class="text-20px">
      {{ getConfig('projectName') }}
    </div>
  </div>
</template>

<style scoped>
.logo-icon {
  background: linear-gradient(
    135deg,
    rgba(var(--primary-6), 0.1) 0%,
    rgba(var(--purple-6), 0.1) 100%
  );
  border: 2px solid rgba(var(--primary-6), 0.2);
  box-shadow: 0 4px 12px rgba(var(--primary-6), 0.15);
  transition: all 0.3s ease;
}

.logo-icon:hover {
  background: linear-gradient(
    135deg,
    rgba(var(--primary-6), 0.2) 0%,
    rgba(var(--purple-6), 0.2) 100%
  );
  border-color: rgba(var(--primary-6), 0.4);
  box-shadow: 0 6px 16px rgba(var(--primary-6), 0.25);
  transform: translateY(-1px);
}
</style>
