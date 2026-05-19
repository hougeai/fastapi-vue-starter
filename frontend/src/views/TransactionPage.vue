<script setup>
import { ref, onMounted } from 'vue'
import { useLedgerStore } from '@/stores/ledger'
import { useTransactionStore } from '@/stores/transaction'

const ledgerStore = useLedgerStore()
const transactionStore = useTransactionStore()

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
      交易记录 - 列表 + 添加
    </div>
  </div>
</template>
