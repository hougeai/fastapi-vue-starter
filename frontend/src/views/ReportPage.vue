<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useLedgerStore } from '@/stores/ledger'
import { useTransactionStore } from '@/stores/transaction'
import api from '@/api'
import dayjs from 'dayjs'

const router = useRouter()
const ledgerStore = useLedgerStore()
const transactionStore = useTransactionStore()

const loading = ref(false)
const currentLedger = computed(() => ledgerStore.currentLedger)
const ledgers = computed(() => ledgerStore.ledgers)
const showLedgerDropdown = ref(false)

// 类别汇总数据
const categoryData = ref([])

// 收入类别汇总
const incomeCategories = computed(() => categoryData.value.filter(c => c.tx_type === 1))
// 支出类别汇总
const expenseCategories = computed(() => categoryData.value.filter(c => c.tx_type === 2))

// 饼图颜色
const pieColors = ['#1668DC', '#0FC6C2', '#FF7D00', '#F53F3F', '#722ED1', '#3491FA', '#F77234', '#D91AD9', '#00B42A', '#FFCD00']

// 获取类别汇总
const fetchCategorySummary = async () => {
  if (!currentLedger.value) return
  let startDate, endDate
  if (reportMode.value === 'month') {
    startDate = dayjs(`${selectedYear.value}-${selectedMonth.value}-01`).startOf('month').format('YYYY-MM-DD')
    endDate = dayjs(`${selectedYear.value}-${selectedMonth.value}-01`).endOf('month').format('YYYY-MM-DD')
  } else {
    startDate = `${selectedYear.value}-01-01`
    endDate = `${selectedYear.value}-12-31`
  }
  try {
    const res = await api.getCategorySummary({
      ledger_id: currentLedger.value.id,
      start_date: startDate,
      end_date: endDate
    })
    if (res.code === 200) {
      categoryData.value = res.data || []
    }
  } catch (e) {
    console.error('获取类别汇总失败:', e)
  }
}

// 饼图 SVG path 计算
const getPiePaths = (items) => {
  if (!items.length) return []
  const total = items.reduce((sum, item) => sum + item.amount, 0)
  if (total <= 0) return []

  const cx = 50, cy = 50, r = 45

  // 单个类别：用两个半圆弧拼成完整圆
  if (items.length === 1) {
    const path = `M ${cx} ${cy} L ${cx} ${cy - r} A ${r} ${r} 0 1 1 ${cx} ${cy + r} A ${r} ${r} 0 1 1 ${cx} ${cy - r} Z`
    return [{ path, color: pieColors[0], item: items[0] }]
  }

  const paths = []
  let startAngle = -Math.PI / 2 // 从12点方向开始

  items.forEach((item, index) => {
    const angle = (item.amount / total) * Math.PI * 2
    const endAngle = startAngle + angle
    const largeArc = angle > Math.PI ? 1 : 0

    const x1 = cx + r * Math.cos(startAngle)
    const y1 = cy + r * Math.sin(startAngle)
    const x2 = cx + r * Math.cos(endAngle)
    const y2 = cy + r * Math.sin(endAngle)

    const path = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`
    paths.push({ path, color: pieColors[index % pieColors.length], item })

    startAngle = endAngle
  })
  return paths
}

// 收入饼图
const incomePiePaths = computed(() => getPiePaths(incomeCategories.value))
// 支出饼图
const expensePiePaths = computed(() => getPiePaths(expenseCategories.value))

// 报表模式：month | year
const reportMode = ref('month')
// 当前选中年份
const selectedYear = ref(dayjs().year())
// 当前选中月份
const selectedMonth = ref(dayjs().month() + 1)

// 月度汇总数据
const monthlyData = ref({
  total_income: 0,
  total_expense: 0,
  balance: 0,
  count: 0
})

// 年度每月汇总
const yearlyData = ref([])

// 金额格式化
const formatMoney = (amount) => {
  return amount != null ? Number(amount).toFixed(2) : '0.00'
}

// 月份名称
const monthNames = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']

// 切换账本
const switchLedger = async (ledger) => {
  ledgerStore.setCurrentLedger(ledger)
  showLedgerDropdown.value = false
  await fetchData()
}

// 获取数据
const fetchData = async () => {
  if (!currentLedger.value) return
  loading.value = true
  try {
    if (reportMode.value === 'month') {
      await fetchMonthlySummary()
    } else {
      await fetchYearlySummary()
    }
    await fetchCategorySummary()
  } finally {
    loading.value = false
  }
}

// 月度汇总
const fetchMonthlySummary = async () => {
  const res = await transactionStore.fetchMonthlySummary(
    currentLedger.value.id,
    selectedYear.value,
    selectedMonth.value
  )
  if (res?.code === 200) {
    monthlyData.value = res.data || { total_income: 0, total_expense: 0, balance: 0, count: 0 }
  }
}

// 年度汇总 - 逐月获取
const fetchYearlySummary = async () => {
  const results = []
  for (let m = 1; m <= 12; m++) {
    const res = await transactionStore.fetchMonthlySummary(
      currentLedger.value.id,
      selectedYear.value,
      m
    )
    const data = res?.data || { total_income: 0, total_expense: 0, balance: 0, count: 0 }
    results.push({
      month: m,
      label: monthNames[m - 1],
      ...data
    })
  }
  yearlyData.value = results
}

// 年度总计
const yearlyTotal = computed(() => {
  const income = yearlyData.value.reduce((sum, m) => sum + (m.total_income || 0), 0)
  const expense = yearlyData.value.reduce((sum, m) => sum + (m.total_expense || 0), 0)
  return {
    total_income: income,
    total_expense: expense,
    balance: income - expense,
    count: yearlyData.value.reduce((sum, m) => sum + (m.count || 0), 0)
  }
})

// 支出占比最高的月份
const topExpenseMonth = computed(() => {
  if (!yearlyData.value.length) return null
  const sorted = [...yearlyData.value].sort((a, b) => (b.total_expense || 0) - (a.total_expense || 0))
  return sorted[0]?.total_expense > 0 ? sorted[0] : null
})

// 上一年
const prevYear = () => {
  selectedYear.value--
  fetchData()
}

// 下一年
const nextYear = () => {
  selectedYear.value++
  fetchData()
}

// 上个月
const prevMonth = () => {
  if (selectedMonth.value === 1) {
    selectedMonth.value = 12
    selectedYear.value--
  } else {
    selectedMonth.value--
  }
  fetchData()
}

// 下个月
const nextMonth = () => {
  if (selectedMonth.value === 12) {
    selectedMonth.value = 1
    selectedYear.value++
  } else {
    selectedMonth.value++
  }
  fetchData()
}

// 月份进度条宽度
const getBarWidth = (value, max) => {
  if (!max) return '0%'
  return `${Math.min((Math.abs(value) / max) * 100, 100)}%`
}

// 年度最大值（收入和支出取最大）
const chartMax = computed(() => {
  if (!yearlyData.value.length) return 1
  const maxIncome = Math.max(...yearlyData.value.map(m => m.total_income || 0))
  const maxExpense = Math.max(...yearlyData.value.map(m => m.total_expense || 0))
  return Math.max(maxIncome, maxExpense, 1)
})

// 柱状图高度计算（最大160px）
const getChartHeight = (value) => {
  if (!value) return 2
  return Math.max((value / chartMax.value) * 160, 2)
}

// 年度最大支出
const maxExpense = computed(() => {
  if (!yearlyData.value.length) return 0
  return Math.max(...yearlyData.value.map(m => m.total_expense || 0), 1)
})

// 初始化
onMounted(async () => {
  if (!ledgerStore.ledgers.length) {
    await ledgerStore.fetchLedgerList()
  }
  if (!currentLedger.value && ledgerStore.ledgers.length) {
    ledgerStore.currentLedger = ledgerStore.ledgers.find(l => l.is_default) || ledgerStore.ledgers[0]
  }
  if (currentLedger.value) {
    await fetchData()
  }
})

// 切换模式时重新获取
watch(reportMode, () => {
  fetchData()
})
</script>

<template>
  <div class="w-full min-h-screen bg-[var(--color-fill-1)]">
    <!-- 顶部区域 -->
    <div class="bg-gradient-to-br from-purple-50 via-violet-50 to-white px-6 pt-6 pb-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-[var(--color-text-1)]">收支报表</h1>
          <a-dropdown v-model:popup-visible="showLedgerDropdown" trigger="click" :disabled="ledgers.length === 0">
            <div class="flex items-center gap-1 cursor-pointer bg-white rounded-full px-3 py-1 shadow-sm border border-[var(--color-border-2)]">
              <icon-material-symbols:account-balance-wallet-outline class="text-sm text-purple-500" />
              <span class="text-sm font-medium text-[var(--color-text-1)]">{{ currentLedger?.name || '请选择' }}</span>
              <icon-material-symbols:keyboard-arrow-down v-if="ledgers.length" class="text-sm text-[var(--color-text-3)]" />
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
        <a-radio-group v-model="reportMode" type="button" size="small">
          <a-radio value="month">月度</a-radio>
          <a-radio value="year">年度</a-radio>
        </a-radio-group>
      </div>
    </div>

    <div class="px-4 pt-4 pb-4">
      <a-spin :loading="loading" class="w-full">
        <template v-if="currentLedger">
          <!-- ====== 月度报表 ====== -->
          <template v-if="reportMode === 'month'">
            <!-- 月份选择 -->
            <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm p-4 mb-4">
              <div class="flex items-center justify-between">
                <a-button type="text" size="small" @click="prevMonth">
                  <template #icon><icon-material-symbols:chevron-left /></template>
                </a-button>
                <span class="text-lg font-semibold text-[var(--color-text-1)]">
                  {{ selectedYear }}年{{ selectedMonth }}月
                </span>
                <a-button type="text" size="small" @click="nextMonth">
                  <template #icon><icon-material-symbols:chevron-right /></template>
                </a-button>
              </div>
            </div>

            <!-- 收支概览 -->
            <div class="grid grid-cols-3 gap-3 mb-4">
              <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm text-center">
                <div class="text-xs text-[var(--color-text-3)] mb-1">收入</div>
                <div class="text-lg font-bold text-green-500">+{{ formatMoney(monthlyData.total_income) }}</div>
              </div>
              <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm text-center">
                <div class="text-xs text-[var(--color-text-3)] mb-1">支出</div>
                <div class="text-lg font-bold text-red-500">-{{ formatMoney(monthlyData.total_expense) }}</div>
              </div>
              <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm text-center">
                <div class="text-xs text-[var(--color-text-3)] mb-1">结余</div>
                <div class="text-lg font-bold text-blue-600">{{ formatMoney(monthlyData.balance) }}</div>
              </div>
            </div>

            <!-- 收支比例 -->
            <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm p-4 mb-4">
              <div class="text-sm font-medium text-[var(--color-text-1)] mb-3">收支比例</div>
              <div class="h-6 rounded-full overflow-hidden bg-[var(--color-fill-2)] flex">
                <div
                  v-if="monthlyData.total_income || monthlyData.total_expense"
                  class="h-full bg-green-400 transition-all duration-300"
                  :style="{ width: `${monthlyData.total_income / ((monthlyData.total_income || 0) + (monthlyData.total_expense || 0)) * 100}%` }"
                />
                <div
                  v-if="monthlyData.total_income || monthlyData.total_expense"
                  class="h-full bg-red-400 transition-all duration-300"
                  :style="{ width: `${monthlyData.total_expense / ((monthlyData.total_income || 0) + (monthlyData.total_expense || 0)) * 100}%` }"
                />
              </div>
              <div class="flex justify-between mt-2 text-xs text-[var(--color-text-3)]">
                <span class="flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-green-400" />
                  收入 {{ monthlyData.total_income > 0 ? Math.round(monthlyData.total_income / ((monthlyData.total_income || 0) + (monthlyData.total_expense || 0)) * 100) : 0 }}%
                </span>
                <span>共 {{ monthlyData.count }} 笔</span>
                <span class="flex items-center gap-1">
                  <span class="w-2 h-2 rounded-full bg-red-400" />
                  支出 {{ monthlyData.total_expense > 0 ? Math.round(monthlyData.total_expense / ((monthlyData.total_income || 0) + (monthlyData.total_expense || 0)) * 100) : 0 }}%
                </span>
              </div>
            </div>

            <!-- 交易笔数 -->
            <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm p-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-[var(--color-text-2)]">本月交易笔数</span>
                <span class="text-2xl font-bold text-[var(--color-text-1)]">{{ monthlyData.count }}</span>
              </div>
              <div class="text-xs text-[var(--color-text-3)] mt-1">
                日均 {{ monthlyData.count ? (monthlyData.count / dayjs(`${selectedYear}-${selectedMonth}-01`).daysInMonth()).toFixed(1) : 0 }} 笔
              </div>
            </div>
          </template>

          <!-- ====== 年度报表 ====== -->
          <template v-else>
            <!-- 年份选择 -->
            <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm p-4 mb-4">
              <div class="flex items-center justify-between">
                <a-button type="text" size="small" @click="prevYear">
                  <template #icon><icon-material-symbols:chevron-left /></template>
                </a-button>
                <span class="text-lg font-semibold text-[var(--color-text-1)]">
                  {{ selectedYear }}年
                </span>
                <a-button type="text" size="small" @click="nextYear">
                  <template #icon><icon-material-symbols:chevron-right /></template>
                </a-button>
              </div>
            </div>

            <!-- 年度汇总 -->
            <div class="grid grid-cols-3 gap-3 mb-4">
              <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm text-center">
                <div class="text-xs text-[var(--color-text-3)] mb-1">年收入</div>
                <div class="text-lg font-bold text-green-500">+{{ formatMoney(yearlyTotal.total_income) }}</div>
              </div>
              <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm text-center">
                <div class="text-xs text-[var(--color-text-3)] mb-1">年支出</div>
                <div class="text-lg font-bold text-red-500">-{{ formatMoney(yearlyTotal.total_expense) }}</div>
              </div>
              <div class="bg-[var(--color-bg-2)] rounded-xl p-4 shadow-sm text-center">
                <div class="text-xs text-[var(--color-text-3)] mb-1">年结余</div>
                <div class="text-lg font-bold text-blue-600">{{ formatMoney(yearlyTotal.balance) }}</div>
              </div>
            </div>

            <!-- 月度支出排行 -->
            <!-- 逐月柱状图 -->
            <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm overflow-hidden">
              <div class="px-4 py-3 border-b border-[var(--color-border-1)]">
                <span class="font-medium text-[var(--color-text-1)]">月度明细</span>
              </div>
              <div class="p-4">
                <!-- 图例 -->
                <div class="flex items-center justify-center gap-4 mb-4 text-xs text-[var(--color-text-3)]">
                  <span class="flex items-center gap-1">
                    <span class="w-3 h-3 rounded-sm bg-green-400" />收入
                  </span>
                  <span class="flex items-center gap-1">
                    <span class="w-3 h-3 rounded-sm bg-red-400" />支出
                  </span>
                </div>
                <!-- 柱状图 -->
                <div class="flex items-end gap-1" style="height: 220px;">
                  <div
                    v-for="m in yearlyData"
                    :key="m.month"
                    class="flex-1 flex flex-col items-center justify-end h-full"
                  >
                    <div class="flex gap-0.5 items-end w-full justify-center" style="height: 160px;">
                      <!-- 收入柱 -->
                      <div class="relative flex flex-col items-center justify-end">
                        <span v-if="m.total_income" class="text-green-500 mb-0.5 whitespace-nowrap" style="font-size: 8px;">{{ m.total_income >= 10000 ? (m.total_income / 10000).toFixed(1) + 'w' : m.total_income.toFixed(0) }}</span>
                        <div
                          class="w-2.5 rounded-t transition-all duration-300 bg-green-400"
                          :style="{ height: `${getChartHeight(m.total_income)}px` }"
                        />
                      </div>
                      <!-- 支出柱 -->
                      <div class="relative flex flex-col items-center justify-end">
                        <span v-if="m.total_expense" class="text-red-500 mb-0.5 whitespace-nowrap" style="font-size: 8px;">{{ m.total_expense >= 10000 ? (m.total_expense / 10000).toFixed(1) + 'w' : m.total_expense.toFixed(0) }}</span>
                        <div
                          class="w-2.5 rounded-t transition-all duration-300 bg-red-400"
                          :style="{ height: `${getChartHeight(m.total_expense)}px` }"
                        />
                      </div>
                    </div>
                    <span class="text-xs text-[var(--color-text-3)] mt-1">{{ m.month }}月</span>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- ====== 类别分析 ====== -->
          <div class="mt-4">
            <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm p-4">
              <div class="text-sm font-medium text-[var(--color-text-1)] mb-4">类别分析</div>
              <div class="grid grid-cols-2 gap-4">
                <!-- 收入类别 -->
                <div>
                  <div class="text-xs text-[var(--color-text-3)] mb-2 text-center">收入构成</div>
                  <div v-if="incomeCategories.length" class="flex items-center justify-center gap-3">
                    <svg viewBox="0 0 100 100" class="w-24 h-24 flex-shrink-0">
                      <path
                        v-for="(seg, idx) in incomePiePaths"
                        :key="idx"
                        :d="seg.path"
                        :fill="seg.color"
                        stroke="white"
                        stroke-width="0.5"
                      />
                    </svg>
                    <div class="space-y-1.5">
                      <div
                        v-for="(cat, idx) in incomeCategories"
                        :key="cat.category_name"
                        class="flex items-center text-xs gap-1"
                      >
                        <span class="w-2 h-2 rounded-full flex-shrink-0" :style="{ backgroundColor: pieColors[idx % pieColors.length] }" />
                        <span class="text-[var(--color-text-2)]">{{ cat.category_name }}</span>
                        <span class="text-[var(--color-text-3)]">{{ ((cat.amount / incomeCategories.reduce((s, c) => s + c.amount, 0)) * 100).toFixed(1) }}%</span>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-6 text-xs text-[var(--color-text-4)]">暂无收入数据</div>
                </div>
                <!-- 支出类别 -->
                <div>
                  <div class="text-xs text-[var(--color-text-3)] mb-2 text-center">支出构成</div>
                  <div v-if="expenseCategories.length" class="flex items-center justify-center gap-3">
                    <svg viewBox="0 0 100 100" class="w-24 h-24 flex-shrink-0">
                      <path
                        v-for="(seg, idx) in expensePiePaths"
                        :key="idx"
                        :d="seg.path"
                        :fill="seg.color"
                        stroke="white"
                        stroke-width="0.5"
                      />
                    </svg>
                    <div class="space-y-1.5">
                      <div
                        v-for="(cat, idx) in expenseCategories"
                        :key="cat.category_name"
                        class="flex items-center text-xs gap-1"
                      >
                        <span class="w-2 h-2 rounded-full flex-shrink-0" :style="{ backgroundColor: pieColors[idx % pieColors.length] }" />
                        <span class="text-[var(--color-text-2)]">{{ cat.category_name }}</span>
                        <span class="text-[var(--color-text-3)]">{{ ((cat.amount / expenseCategories.reduce((s, c) => s + c.amount, 0)) * 100).toFixed(1) }}%</span>
                      </div>
                    </div>
                  </div>
                  <div v-else class="text-center py-6 text-xs text-[var(--color-text-4)]">暂无支出数据</div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- 无账本 -->
        <div v-else class="bg-[var(--color-bg-2)] rounded-xl p-8 shadow-sm text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-purple-100 flex items-center justify-center">
            <icon-material-symbols:account-balance-wallet-outline class="text-3xl text-purple-500" />
          </div>
          <h3 class="text-lg font-semibold text-[var(--color-text-1)] mb-2">请先选择账本</h3>
          <p class="text-sm text-[var(--color-text-3)] mb-6">选择一个账本后即可查看报表</p>
          <a-button type="primary" @click="router.push('/ledgers')">去管理账本</a-button>
        </div>
      </a-spin>
    </div>
  </div>
</template>
