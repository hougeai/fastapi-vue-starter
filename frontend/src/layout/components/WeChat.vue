<script setup>
import { getConfig } from '@/config'
</script>

<template>
  <a-trigger
    position="bottom"
    auto-fit-position
    :unmount-on-close="false"
    :popup-offset="10"
    :show-arrow="true"
  >
    <a-button type="text" size="large" class="nav-btn">
      <template #icon>
        <icon-ic:baseline-wechat class="text-[var(--color-text-1)] text-18px" />
      </template>
    </a-button>
    <template #content>
      <div class="p-3">
        <a-image width="200" :src="getConfig('me.gzhUrl')" />
        <p class="text-center text-xs text-gray-600 mt-2">
          {{ getConfig('me.gzhName') }}
        </p>
      </div>
    </template>
  </a-trigger>
</template>
