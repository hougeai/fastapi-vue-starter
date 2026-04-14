<script setup>
import { getConfig } from '@/config'
const openNewWindow = () => window.open(getConfig('me.feishuDoc'), '_blank')
</script>

<template>
  <a-button type="text" @click="openNewWindow">
    <div class="flex items-center justify-center">
      <icon-mdi-file-document class="text-lg text-[var(--color-primary-1)]" />
      <span class="font-bold text-lg text-[var(--color-primary-1)] ml-1">使用教程</span>
    </div>
  </a-button>
</template>
