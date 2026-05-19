<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLedgerStore } from '@/stores/ledger'
import { useTransactionStore } from '@/stores/transaction'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const router = useRouter()
const ledgerStore = useLedgerStore()
const transactionStore = useTransactionStore()
const userStore = useUserStore()

const loading = ref(false)
const showLedgerDropdown = ref(false)

const currentLedger = computed(() => ledgerStore.currentLedger)
const ledgers = computed(() => ledgerStore.ledgers)
const summary = computed(() => transactionStore.summary)

const formatMoney = (amount) => {
  return amount != null ? Number(amount).toFixed(2) : '0.00'
}

const switchLedger = (ledger) => {
  ledgerStore.setCurrentLedger(ledger)
  showLedgerDropdown.value = false
  if (ledger) fetchData()
}

const fetchData = async () => {
  if (!currentLedger.value) return
  loading.value = true
  try {
    await Promise.all([
      transactionStore.fetchTransactions({ ledgerId: currentLedger.value.id, pageSize: 5 }),
      transactionStore.fetchSummary(currentLedger.value.id)
    ])
  } finally {
    loading.value = false
  }
}

const getTxTypeLabel = (type) => (type === 1 ? '收入' : '支出')
const getTxTypeColor = (type) => (type === 1 ? 'green' : 'red')

onMounted(async () => {
  loading.value = true
  await Promise.all([
    ledgerStore.fetchLedgerList(),
    userStore.getUserInfo()
  ])
  if (currentLedger.value) await fetchData()
  loading.value = false
})
</script>

<template>
  <div class="w-full min-h-screen bg-[var(--color-fill-1)]">
    <!-- 顶部区域 -->
    <div class="bg-gradient-to-br from-blue-50 via-indigo-50 to-white px-6 pt-8 pb-16">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-xl font-bold text-[var(--color-text-1)]">
            {{ dayjs().format('MM月DD日') }} · 周{{ ['日', '一', '二', '三', '四', '五', '六'][dayjs().day()] }}
          </h1>
          <p class="text-sm text-[var(--color-text-3)] mt-1">{{ userStore.userName || '用户' }}，今天想记点什么？</p>
        </div>
        <a-button type="primary" shape="round" :disabled="!currentLedger" @click="router.push('/transactions')">
          <template #icon><icon-material-symbols:add /></template>
          记一笔
        </a-button>
      </div>

      <!-- 账本选择 -->
      <a-dropdown v-model:popup-visible="showLedgerDropdown" trigger="click" :disabled="ledgers.length === 0">
        <div class="flex items-center gap-1 cursor-pointer bg-white rounded-full px-4 py-1.5 shadow-sm border border-[var(--color-border-2)] w-fit">
          <icon-material-symbols:account-balance-wallet-outline class="text-base text-blue-500" />
          <span class="text-sm font-medium text-[var(--color-text-1)]">{{ currentLedger?.name || '请选择账本' }}</span>
          <icon-material-symbols:keyboard-arrow-down v-if="ledgers.length" class="text-base text-[var(--color-text-3)]" />
        </div>
        <template #content>
          <a-doption
            v-for="ledger in ledgers"
            :key="ledger.id"
            @click="switchLedger(ledger)"
          >
            <div class="flex items-center justify-between w-full">
              <span>{{ ledger.name }}</span>
              <a-tag v-if="ledger.is_default" size="small" color="arcoblue">默认</a-tag>
            </div>
          </a-doption>
        </template>
      </a-dropdown>
    </div>

    <!-- 无账本引导 -->
    <div v-if="!loading && ledgers.length === 0" class="px-4 -mt-10 mb-4">
      <div class="bg-[var(--color-bg-2)] rounded-xl p-8 shadow-sm text-center">
        <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-100 flex items-center justify-center">
          <icon-material-symbols:book-2-outline class="text-3xl text-blue-500" />
        </div>
        <h3 class="text-lg font-semibold text-[var(--color-text-1)] mb-2">还没有账本</h3>
        <p class="text-sm text-[var(--color-text-3)] mb-6">创建一个账本，开始记录你的收支吧</p>
        <div class="flex justify-center gap-3">
          <a-button type="primary" @click="router.push('/ledgers')">
            <template #icon><icon-material-symbols:add /></template>
            创建账本
          </a-button>
          <a-button type="outline" @click="router.push('/ledgers')">
            <template #icon><icon-material-symbols:dashboard-customize-outline /></template>
            从模板创建
          </a-button>
        </div>
      </div>
    </div>

    <!-- 有账本时的内容 -->
    <template v-else>
      <!-- 收支概览 -->
      <div class="px-4 -mt-10 mb-4">
        <div class="grid grid-cols-3 gap-3">
          <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm">
            <div class="text-xs text-[var(--color-text-3)] mb-1">本月收入</div>
            <div class="text-lg font-bold text-green-500">+{{ formatMoney(summary.total_income) }}</div>
          </div>
          <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm">
            <div class="text-xs text-[var(--color-text-3)] mb-1">本月支出</div>
            <div class="text-lg font-bold text-red-500">-{{ formatMoney(summary.total_expense) }}</div>
          </div>
          <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm">
            <div class="text-xs text-[var(--color-text-3)] mb-1">本月结余</div>
            <div class="text-lg font-bold text-blue-600">{{ formatMoney(summary.balance) }}</div>
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <div class="px-4 mb-4">
        <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm">
          <div class="grid grid-cols-4 gap-2">
            <div
              class="flex flex-col items-center py-3 rounded-lg cursor-pointer transition-all hover:bg-[var(--color-fill-2)]"
              @click="router.push('/transactions')"
            >
              <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mb-2">
                <icon-material-symbols:edit-note class="text-xl text-blue-500" />
              </div>
              <span class="text-xs text-[var(--color-text-2)]">记一笔</span>
            </div>
            <div
              class="flex flex-col items-center py-3 rounded-lg cursor-pointer transition-all hover:bg-[var(--color-fill-2)]"
              @click="router.push('/ledgers')"
            >
              <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center mb-2">
                <icon-material-symbols:account-balance-wallet-outline class="text-xl text-green-500" />
              </div>
              <span class="text-xs text-[var(--color-text-2)]">账本</span>
            </div>
            <div
              class="flex flex-col items-center py-3 rounded-lg cursor-pointer transition-all hover:bg-[var(--color-fill-2)]"
              @click="router.push('/reports')"
            >
              <div class="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center mb-2">
                <icon-ep:data-analysis class="text-xl text-orange-500" />
              </div>
              <span class="text-xs text-[var(--color-text-2)]">报表</span>
            </div>
            <div
              class="flex flex-col items-center py-3 rounded-lg cursor-pointer transition-all hover:bg-[var(--color-fill-2)]"
              @click="router.push('/ledgers')"
            >
              <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center mb-2">
                <icon-material-symbols:dashboard-customize-outline class="text-xl text-purple-500" />
              </div>
              <span class="text-xs text-[var(--color-text-2)]">模板</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近交易 -->
      <div class="px-4 mb-4">
        <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border-1)]">
            <span class="font-medium text-[var(--color-text-1)]">最近交易</span>
            <a-link @click="router.push('/transactions')">查看全部</a-link>
          </div>

          <a-spin :loading="loading" class="w-full">
            <div v-if="transactionStore.transactions.length">
              <div
                v-for="tx in transactionStore.transactions"
                :key="tx.id"
                class="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border-1)] last:border-0 hover:bg-[var(--color-fill-2)] transition-colors"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                    :class="tx.tx_type === 1 ? 'bg-green-100 text-green-500' : 'bg-red-100 text-red-500'"
                  >
                    {{ tx.tx_type === 1 ? '收' : '支' }}
                  </div>
                  <div>
                    <div class="text-sm text-[var(--color-text-1)]">{{ tx.remark || '无备注' }}</div>
                    <div class="text-xs text-[var(--color-text-3)] mt-0.5">{{ tx.tx_date }}</div>
                  </div>
                </div>
                <div
                  class="text-sm font-semibold"
                  :class="tx.tx_type === 1 ? 'text-green-500' : 'text-red-500'"
                >
                  {{ tx.tx_type === 1 ? '+' : '-' }}¥{{ formatMoney(tx.amount) }}
                </div>
              </div>
            </div>

            <div v-else class="py-12 text-center">
              <icon-material-symbols:receipt-long-outline class="text-4xl text-[var(--color-text-4)] mb-2" />
              <p class="text-sm text-[var(--color-text-3)]">暂无交易记录</p>
              <a-button type="text" size="small" @click="router.push('/transactions')">去记一笔</a-button>
            </div>
          </a-spin>
        </div>
      </div>
    </template>
  </div>
</template>
