<script setup>
import { getConfig } from '@/config'
</script>
<template>
  <div class="w-full flex justify-center items-center space-x-2 py-4">
    <span>Copyright ⓒ 2025-2030</span>
    <a-link :href="getConfig('me.github')" target="_blank">
      {{ getConfig('me.name') }}
    </a-link>
    <a-link href="https://beian.miit.gov.cn/" target="_blank">
      {{ getConfig('me.icp') }}
    </a-link>
  </div>
</template>
