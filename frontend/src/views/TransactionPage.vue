<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLedgerStore } from '@/stores/ledger'
import { useTransactionStore } from '@/stores/transaction'
import { Message } from '@arco-design/web-vue'
import dayjs from 'dayjs'

const router = useRouter()
const ledgerStore = useLedgerStore()
const transactionStore = useTransactionStore()

const loading = computed(() => transactionStore.loading)
const transactions = computed(() => transactionStore.transactions)
const total = computed(() => transactionStore.total)
const currentLedger = computed(() => ledgerStore.currentLedger)
const ledgers = computed(() => ledgerStore.ledgers)
const categories = computed(() => ledgerStore.categories)

// 筛选条件
const filterTxType = ref(0) // 0=全部, 1=收入, 2=支出
const showLedgerDropdown = ref(false)
const filterMonth = ref('')
const filterDay = ref('')
const filterMode = ref('month') // month | day
const pagination = computed(() => ({
  current: transactionStore.page,
  pageSize: transactionStore.pageSize,
  total: total.value
}))

// 弹窗相关
const showModal = ref(false)
const modalMode = ref('create') // create | edit
const formRef = ref()
const submitLoading = ref(false)

// 表单
const form = ref({
  id: null,
  tx_type: 2,
  amount: null,
  category_id: null,
  tx_date: dayjs().format('YYYY-MM-DD'),
  remark: ''
})

const formRules = {
  tx_type: [{ required: true, message: '请选择类型' }],
  amount: [{ required: true, message: '请输入金额' }],
  tx_date: [{ required: true, message: '请选择日期' }]
}

// 金额格式化
const formatMoney = (amount) => {
  return amount != null ? Number(amount).toFixed(2) : '0.00'
}

// 获取类别名称
const getCategoryName = (categoryId) => {
  const cat = categories.value.find(c => c.id === categoryId)
  return cat?.name || '未分类'
}

// 筛选后的类别
const filteredCategories = computed(() => {
  if (!form.value.tx_type) return categories.value
  return categories.value.filter(c => c.tx_type === form.value.tx_type)
})

// 获取数据
const fetchData = async () => {
  if (!currentLedger.value) return
  const params = {
    ledgerId: currentLedger.value.id,
    page: pagination.value.current,
    txType: filterTxType.value || null
  }
  if (filterMode.value === 'month' && filterMonth.value) {
    const d = dayjs(filterMonth.value)
    params.startDate = d.startOf('month').format('YYYY-MM-DD')
    params.endDate = d.endOf('month').format('YYYY-MM-DD')
  } else if (filterMode.value === 'day' && filterDay.value) {
    params.startDate = filterDay.value
    params.endDate = filterDay.value
  }
  await transactionStore.fetchTransactions(params)
}

// 切换筛选类型
const handleFilterChange = async (type) => {
  filterTxType.value = type
  await fetchData()
}

// 切换日期筛选模式
const handleFilterModeChange = async (mode) => {
  filterMode.value = mode
  filterMonth.value = ''
  filterDay.value = ''
  await fetchData()
}

// 切换月份/日期
const handleDateChange = async () => {
  await fetchData()
}

// 分页
const handlePageChange = async (page) => {
  transactionStore.page = page
  await fetchData()
}

// 打开创建弹窗
const openCreateModal = async () => {
  if (!currentLedger.value) {
    Message.warning('请先选择账本')
    return
  }
  modalMode.value = 'create'
  form.value = {
    id: null,
    tx_type: 2,
    amount: null,
    category_id: null,
    tx_date: dayjs().format('YYYY-MM-DD'),
    remark: ''
  }
  await ledgerStore.fetchCategories()
  showModal.value = true
}

// 打开编辑弹窗
const openEditModal = async (tx) => {
  modalMode.value = 'edit'
  form.value = {
    id: tx.id,
    tx_type: tx.tx_type,
    amount: tx.amount,
    category_id: tx.category_id,
    tx_date: tx.tx_date,
    remark: tx.remark || ''
  }
  await ledgerStore.fetchCategories()
  showModal.value = true
}

// 切换收入/支出
const handleTxTypeChange = () => {
  form.value.category_id = null
}

// 切换账本
const switchLedger = async (ledger) => {
  ledgerStore.setCurrentLedger(ledger)
  showLedgerDropdown.value = false
  await ledgerStore.fetchCategories()
  await fetchData()
}

// 提交表单
const handleSubmit = async () => {
  try {
    const errors = await formRef.value?.validate()
    if (errors) return
    submitLoading.value = true
    const data = {
      ledger_id: currentLedger.value.id,
      tx_type: form.value.tx_type,
      amount: form.value.amount,
      category_id: form.value.category_id,
      tx_date: form.value.tx_date,
      remark: form.value.remark
    }
    if (modalMode.value === 'create') {
      const res = await transactionStore.createTransaction(data)
      if (res?.code === 200) {
        Message.success('添加成功')
        showModal.value = false
      } else {
        Message.error(res?.msg || '添加失败')
      }
    } else {
      const { id, ...updateData } = form.value
      const res = await transactionStore.updateTransaction(id, updateData)
      if (res?.code === 200) {
        Message.success('更新成功')
        showModal.value = false
      } else {
        Message.error(res?.msg || '更新失败')
      }
    }
    await fetchData()
  } catch (e) {
    Message.error(e?.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

// 删除交易
const handleDelete = (tx) => {
  AModal.confirm({
    title: '删除交易',
    content: `确定要删除这笔「${tx.remark || '无备注'}」的${tx.tx_type === 1 ? '收入' : '支出'}记录吗？`,
    okText: '删除',
    cancelText: '取消',
    okButtonProps: { status: 'danger' },
    onOk: async () => {
      const res = await transactionStore.deleteTransaction(tx.id)
      if (res?.code === 200) {
        Message.success('删除成功')
        await fetchData()
      } else {
        Message.error(res?.msg || '删除失败')
      }
    }
  })
}

// 初始化
onMounted(async () => {
  if (!ledgerStore.ledgers.length) {
    await ledgerStore.fetchLedgerList()
  }
  // 确保 currentLedger 有效
  if (!currentLedger.value && ledgerStore.ledgers.length) {
    ledgerStore.currentLedger = ledgerStore.ledgers.find(l => l.is_default) || ledgerStore.ledgers[0]
  }
  if (currentLedger.value) {
    await ledgerStore.fetchCategories()
    await fetchData()
  }
})
</script>

<template>
  <div class="w-full min-h-screen bg-[var(--color-fill-1)]">
    <!-- 顶部区域 -->
    <div class="bg-gradient-to-br from-orange-50 via-amber-50 to-white px-6 pt-6 pb-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-[var(--color-text-1)]">交易记录</h1>
          <a-dropdown v-model:popup-visible="showLedgerDropdown" trigger="click" :disabled="ledgers.length === 0">
            <div class="flex items-center gap-1 cursor-pointer bg-white rounded-full px-3 py-1 shadow-sm border border-[var(--color-border-2)]">
              <icon-material-symbols:account-balance-wallet-outline class="text-sm text-orange-500" />
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
        <a-button type="primary" :disabled="!currentLedger" @click="openCreateModal">
          <template #icon><icon-material-symbols:add /></template>
          记一笔
        </a-button>
      </div>

      <!-- 筛选栏 -->
      <div class="flex items-center gap-3 mt-4 flex-wrap">
        <a-radio-group v-model="filterTxType" type="button" size="small" @change="handleFilterChange">
          <a-radio :value="0">全部</a-radio>
          <a-radio :value="1">收入</a-radio>
          <a-radio :value="2">支出</a-radio>
        </a-radio-group>
        <a-radio-group v-model="filterMode" type="button" size="small" @change="handleFilterModeChange">
          <a-radio value="month">按月</a-radio>
          <a-radio value="day">按日</a-radio>
        </a-radio-group>
        <a-date-picker
          v-if="filterMode === 'month'"
          v-model="filterMonth"
          size="small"
          format="YYYY-MM"
          @change="handleDateChange"
          style="width: 140px"
          placeholder="选择月份"
          allow-clear
        />
        <a-date-picker
          v-else
          v-model="filterDay"
          size="small"
          format="YYYY-MM-DD"
          @change="handleDateChange"
          style="width: 160px"
          placeholder="选择日期"
          allow-clear
        />
      </div>
    </div>

    <!-- 交易列表 -->
    <div class="px-4 pt-4 pb-4">
      <a-spin :loading="loading" class="w-full">
        <!-- 有交易记录 -->
        <div v-if="transactions.length">
          <div class="bg-[var(--color-bg-2)] rounded-xl shadow-sm overflow-hidden">
            <div
              v-for="(tx, index) in transactions"
              :key="tx.id"
              class="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border-1)] last:border-0 hover:bg-[var(--color-fill-2)] transition-colors"
            >
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <div
                  class="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                  :class="tx.tx_type === 1 ? 'bg-green-100 text-green-500' : 'bg-red-100 text-red-500'"
                >
                  {{ tx.tx_type === 1 ? '收' : '支' }}
                </div>
                <div class="min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-sm text-[var(--color-text-1)]">{{ tx.remark || '无备注' }}</span>
                    <span class="text-xs px-1.5 py-0.5 rounded bg-[var(--color-fill-2)] text-[var(--color-text-3)]">
                      {{ getCategoryName(tx.category_id) }}
                    </span>
                  </div>
                  <div class="text-xs text-[var(--color-text-3)] mt-0.5">{{ tx.tx_date }}</div>
                </div>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <div
                  class="text-sm font-semibold"
                  :class="tx.tx_type === 1 ? 'text-green-500' : 'text-red-500'"
                >
                  {{ tx.tx_type === 1 ? '+' : '-' }}¥{{ formatMoney(tx.amount) }}
                </div>
                <a-dropdown trigger="click" position="br">
                  <a-button type="text" size="mini">
                    <template #icon><icon-material-symbols:more-vert /></template>
                  </a-button>
                  <template #content>
                    <a-doption @click="openEditModal(tx)">
                      <icon-material-symbols:edit-outline class="mr-1" />编辑
                    </a-doption>
                    <a-doption class="text-red-500" @click="handleDelete(tx)">
                      <icon-material-symbols:delete-outline class="mr-1" />删除
                    </a-doption>
                  </template>
                </a-dropdown>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="total > pagination.pageSize" class="flex justify-center mt-4">
            <a-pagination
              :current="pagination.current"
              :page-size="pagination.pageSize"
              :total="total"
              size="small"
              @change="handlePageChange"
            />
          </div>
        </div>

        <!-- 无交易记录 -->
        <div v-else class="bg-[var(--color-bg-2)] rounded-xl p-8 shadow-sm text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-orange-100 flex items-center justify-center">
            <icon-material-symbols:receipt-long-outline class="text-3xl text-orange-500" />
          </div>
          <h3 class="text-lg font-semibold text-[var(--color-text-1)] mb-2">暂无交易记录</h3>
          <p class="text-sm text-[var(--color-text-3)] mb-6">快记一笔，开始记录你的收支吧</p>
          <a-button type="primary" :disabled="!currentLedger" @click="openCreateModal">
            <template #icon><icon-material-symbols:add /></template>
            记一笔
          </a-button>
        </div>
      </a-spin>
    </div>

    <!-- 新增/编辑交易弹窗 -->
    <a-modal
      v-model:visible="showModal"
      :title="modalMode === 'create' ? '记一笔' : '编辑交易'"
      :mask-closable="false"
      @ok="handleSubmit"
      :ok-loading="submitLoading"
      ok-text="保存"
    >
      <a-form ref="formRef" :model="form" :rules="formRules" layout="vertical">
        <!-- 当前账本 -->
        <a-form-item v-if="modalMode === 'create'" label="记账账本">
          <a-input :model-value="currentLedger?.name" disabled />
        </a-form-item>

        <!-- 收入/支出切换 -->
        <a-form-item field="tx_type" label="类型">
          <a-radio-group v-model="form.tx_type" type="button" @change="handleTxTypeChange">
            <a-radio :value="1">
              <span class="text-green-500">收入</span>
            </a-radio>
            <a-radio :value="2">
              <span class="text-red-500">支出</span>
            </a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item field="amount" label="金额">
          <a-input-number
            v-model="form.amount"
            placeholder="请输入金额"
            :precision="2"
            :min="0.01"
            :step="10"
            hide-button
            style="width: 100%"
          >
            <template #prefix>
              <span class="text-[var(--color-text-3)]">¥</span>
            </template>
          </a-input-number>
        </a-form-item>

        <a-form-item field="category_id" label="类别">
          <a-select v-model="form.category_id" placeholder="请选择类别（可选）" allow-clear>
            <a-option v-for="cat in filteredCategories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </a-option>
          </a-select>
        </a-form-item>

        <a-form-item field="tx_date" label="日期">
          <a-date-picker
            v-model="form.tx_date"
            style="width: 100%"
            placeholder="请选择日期"
          />
        </a-form-item>

        <a-form-item field="remark" label="备注">
          <a-textarea
            v-model="form.remark"
            placeholder="请输入备注（可选）"
            :max-length="200"
            :auto-size="{ minRows: 2, maxRows: 4 }"
            allow-clear
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>
