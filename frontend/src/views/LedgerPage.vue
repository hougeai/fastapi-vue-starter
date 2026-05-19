<script setup>
import { ref, onMounted } from 'vue'
import { useLedgerStore } from '@/stores/ledger'

const ledgerStore = useLedgerStore()

const loading = ref(false)

onMounted(async () => {
  loading.value = true
  await ledgerStore.fetchLedgerList()
  loading.value = false
})
</script>

<template>
  <div class="w-full p-6 bg-[var(--color-fill-0)] min-h-screen">
    <div class="text-center text-gray-400">
      账本管理 - 账本列表、手动创建、模板创建
    </div>
  </div>
</template>
