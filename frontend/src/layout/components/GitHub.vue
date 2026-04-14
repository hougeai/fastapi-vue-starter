<script setup>
import { getConfig } from '@/config'
const openNewWindow = () => window.open(getConfig('me.github'), '_blank')
</script>
<template>
  <a-button type="text" @click="openNewWindow">
    <template #icon>
      <icon-mdi-github class="text-[var(--color-text-1)] text-18px" />
    </template>
  </a-button>
</template>
