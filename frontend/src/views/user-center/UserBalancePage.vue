<template>
  <div class="w-full h-full flex flex-col">
    <!-- 标题与刷新 -->
    <div class="flex items-center gap-3 m-4">
      <div class="text-xl font-bold">余额充值</div>
      <a-button type="outline" size="large" shape="round" :loading="loading" @click="refreshAll">
        <template #icon><icon-material-symbols:refresh /></template>
        刷新
      </a-button>
    </div>

    <!-- 账户余额统计 -->
    <div class="mx-4 mb-4">
      <div
        class="bg-gradient-to-br from-blue-50 to-purple-50/30 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden p-4"
      >
        <div class="text-lg font-semibold mb-4">账户余额</div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div
            class="rounded-xl p-3 text-center"
            style="
              background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
              border: 1px solid var(--color-neutral-3);
            "
          >
            <div class="text-gray-500 text-xs mb-1">总余额</div>
            <div class="text-2xl font-extrabold text-gray-900 leading-none">
              ¥{{ formatMoney(financeStore.balance.total) }}
            </div>
          </div>
          <div
            class="rounded-xl p-3 text-center"
            style="
              background: linear-gradient(180deg, #f7fffb 0%, #ffffff 100%);
              border: 1px solid var(--color-neutral-3);
            "
          >
            <div class="text-gray-500 text-xs mb-1">充值金额</div>
            <div class="text-2xl font-extrabold text-gray-900 leading-none">
              ¥{{ formatMoney(financeStore.balance.recharge) }}
            </div>
          </div>
          <div
            class="rounded-xl p-3 text-center"
            style="
              background: linear-gradient(180deg, #fff9f2 0%, #ffffff 100%);
              border: 1px solid var(--color-neutral-3);
            "
          >
            <div class="text-gray-500 text-xs mb-1">赠送金额</div>
            <div class="text-2xl font-extrabold text-gray-900 leading-none">
              ¥{{ formatMoney(financeStore.balance.gift) }}
            </div>
          </div>
          <div
            class="rounded-xl p-3 text-center"
            style="
              background: linear-gradient(180deg, #f9f9ff 0%, #ffffff 100%);
              border: 1px solid var(--color-neutral-3);
            "
          >
            <div class="text-gray-500 text-xs mb-1">消费总额</div>
            <div class="text-2xl font-extrabold text-gray-900 leading-none">
              ¥{{ formatMoney(financeStore.balance.consume) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 在线充值 & 兑换码充值 -->
    <div class="mx-4 mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 在线充值 -->
      <div
        class="bg-gradient-to-br from-blue-50 to-purple-50/30 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden p-4"
      >
        <div class="text-lg font-semibold mb-3">在线充值</div>
        <div class="flex flex-col gap-4">
          <!-- 支付金额 -->
          <div>
            <div class="text-sm text-gray-600 mb-2">支付金额</div>
            <div class="flex flex-wrap gap-2">
              <div
                v-for="amt in amountPresets"
                :key="amt.key"
                :class="[
                  'px-4 py-2 rounded-xl cursor-pointer select-none',
                  selectedAmountKey === amt.key
                    ? 'border border-solid border-[var(--color-primary-light-4)] bg-[var(--color-primary-light-2)] text-[var(--color-text-1)]'
                    : 'bg-[var(--color-fill-2)] hover:bg-[var(--color-fill-3)]'
                ]"
                @click="selectAmount(amt)"
              >
                {{ amt.label }}
              </div>
            </div>
            <div v-if="selectedAmountKey === 'custom'" class="mt-3">
              <a-input-number
                v-model="customAmount"
                :min="0.01"
                :precision="2"
                placeholder="请输入自定义金额"
              />
            </div>
          </div>

          <!-- 支付方式 -->
          <div>
            <div class="text-sm text-gray-600 mb-2">支付方式</div>
            <div class="flex gap-2">
              <div
                v-for="method in paymentMethods"
                :key="method.key"
                :class="[
                  'px-4 py-2 rounded-xl cursor-pointer select-none flex items-center gap-2',
                  payMethod === method.key
                    ? 'border border-solid border-[var(--color-primary-light-4)] bg-[var(--color-primary-light-2)] text-[var(--color-text-1)]'
                    : 'bg-[var(--color-fill-2)] hover:bg-[var(--color-fill-3)]'
                ]"
                @click="payMethod = method.key"
              >
                <icon-mingcute:wechat-pay-fill
                  v-if="method.key === 'wechat'"
                  :class="method.iconClass"
                />
                <icon-mingcute:alipay-fill
                  v-if="method.key === 'alipay'"
                  :class="method.iconClass"
                />
                {{ method.label }}
              </div>
            </div>
          </div>

          <a-button
            type="primary"
            shape="round"
            :loading="creatingOrder"
            @click="onCreateOrder"
            :disabled="!agreedToTerms"
            >确认支付</a-button
          >
          <a-checkbox v-model="agreedToTerms" class="text-xs text-gray-400">
            我已知悉虚拟产品不支持退款，充值资金不支持直接开具发票。
          </a-checkbox>
        </div>
      </div>
      <!-- 兑换码充值 -->
      <div
        class="bg-gradient-to-br from-blue-50 to-purple-50/30 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden p-4"
      >
        <div class="text-lg font-semibold mb-3">兑换码充值</div>
        <div class="flex flex-col gap-3">
          <a-input v-model="redeemCode" placeholder="请输入兑换码" allow-clear />
          <a-button type="primary" :loading="redeemLoading" @click="onRedeem" shape="round"
            >立即兑换</a-button
          >
          <div class="text-xs text-[var(--color-text-4)]">成功兑换后，余额将自动增加（赠送）</div>
        </div>
      </div>
    </div>

    <!-- 充值记录 & 账单流水 -->
    <div class="flex-1 mx-4 mb-4">
      <a-card class="h-full w-full">
        <a-tabs v-model:active-key="activeTab">
          <a-tab-pane key="recharge">
            <template #title>
              <span class="text-lg font-bold">充值记录</span>
            </template>
            <div class="p-3">
              <a-table
                :columns="rechargeColumns"
                :data="financeStore.rechargeList"
                :loading="loading"
                :bordered="true"
                :stripe="true"
                row-key="id"
                :pagination="false"
              />
            </div>
          </a-tab-pane>
          <a-tab-pane key="flow">
            <template #title>
              <span class="text-lg font-bold">账单流水</span>
            </template>
            <div class="p-3">
              <a-table
                :columns="flowColumns"
                :data="financeStore.flowList"
                :loading="loading"
                :bordered="true"
                :stripe="true"
                row-key="id"
                :pagination="false"
              />
            </div>
          </a-tab-pane>
        </a-tabs>

        <div class="flex justify-center gap-4 pb-4">
          <a-pagination
            v-if="activeTab === 'recharge'"
            v-model:current="financeStore.rechargePage.current"
            v-model:page-size="financeStore.rechargePage.pageSize"
            :total="financeStore.rechargePage.total"
            @change="handleRechargePageChange"
            @page-size-change="handleRechargePageSizeChange"
          />
          <a-pagination
            v-else
            v-model:current="financeStore.flowPage.current"
            v-model:page-size="financeStore.flowPage.pageSize"
            :total="financeStore.flowPage.total"
            @change="handleFlowPageChange"
            @page-size-change="handleFlowPageSizeChange"
          />
        </div>
      </a-card>
    </div>

    <!-- 支付二维码弹窗 -->
    <a-modal
      v-model:visible="qrcodeVisible"
      :mask-closable="false"
      :esc-to-close="false"
      :closable="true"
      :footer="false"
      width="420px"
      @cancel="onQrcodeCancel"
    >
      <template #title>{{ payMethod === 'wechat' ? '微信支付' : '支付宝支付' }}</template>
      <div class="flex flex-col items-center gap-3 py-2">
        <QRCode
          v-if="qrcodeUrl && payMethod !== 'wechat'"
          :value="qrcodeUrl"
          :size="224"
          level="H"
          class="border rounded-lg"
        />
        <img
          v-else-if="payMethod === 'wechat'"
          :src="qrcodeUrl"
          class="w-56 h-56 border rounded-lg"
          alt="qrcode"
        />
        <div v-if="payMethod === 'alipay'" class="text-sm text-gray-600">
          请使用手机打开{{ payMethod === 'wechat' ? '微信' : '支付宝' }}扫描二维码完成支付
        </div>
        <div v-else class="text-sm text-gray-600">
          当前微信支付接口暂未接入，可选择支付宝支付，或加客服微信索要兑换码充值
        </div>
        <a-button type="primary" shape="round" :loading="financeStore.polling" @click="onPaidCheck"
          >已完成支付</a-button
        >
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, h } from 'vue'
import QRCode from 'qrcode.vue'
import { useUserStore } from '@/stores/user'
import { useFinanceStore } from '@/stores/finance'
import { formatDateTime, formatMoney } from '@/utils'

const userStore = useUserStore()
const financeStore = useFinanceStore()
const userId = computed(() => userStore.userId)
const loading = computed(() => financeStore.loading)

onMounted(async () => {
  try {
    if (!userId.value) await userStore.getUserInfo()
    await Promise.all([
      financeStore.fetchBalance(userId.value),
      financeStore.fetchRechargeList(userId.value),
      financeStore.fetchFlowList(userId.value)
    ])
  } catch (e) {
    console.error(e)
    AMessage.error('页面初始化失败')
  }
})

// 兑换
const redeemCode = ref('')
const redeemLoading = ref(false)
const onRedeem = async () => {
  if (!redeemCode.value) return AMessage.warning('请输入兑换码')
  const trimmedCode = redeemCode.value.trim()
  if (!trimmedCode) return AMessage.warning('请输入有效的兑换码')
  if (!userId.value) await userStore.getUserInfo()
  redeemLoading.value = true
  try {
    await financeStore.redeemCode({ userId: userId.value, code: trimmedCode })
    AMessage.success('兑换成功')
    redeemCode.value = ''
    await Promise.all([
      financeStore.fetchBalance(userId.value, true),
      financeStore.fetchFlowList(userId.value, true)
    ])
  } catch (e) {
    AMessage.error(e?.message || '兑换失败')
  } finally {
    redeemLoading.value = false
  }
}

// 在线充值
const amountPresets = [
  { key: '9_9', label: '¥9.9', value: 9.9 },
  { key: '29_9', label: '¥29.9', value: 29.9 },
  { key: '99_9', label: '¥99.9', value: 99.9 },
  { key: '299_9', label: '¥299.9', value: 299.9 },
  { key: 'custom', label: '自定义金额', value: null }
]
const paymentMethods = [
  {
    key: 'wechat',
    label: '微信',
    iconClass: 'text-green-600'
  },
  {
    key: 'alipay',
    label: '支付宝',
    iconClass: 'text-blue-600'
  }
]
const selectedAmountKey = ref(null)
const customAmount = ref(null)
const payMethod = ref('alipay')
const creatingOrder = ref(false)
const agreedToTerms = ref(false)
const qrcodeVisible = ref(false)
const qrcodeUrl = ref('')
const currentOrderId = ref('')

const selectAmount = amt => {
  selectedAmountKey.value = amt.key
}
const resolveAmount = () => {
  if (selectedAmountKey.value === 'custom') return Number(customAmount.value || 0)
  const item = amountPresets.find(i => i.key === selectedAmountKey.value)
  return Number(item?.value || 0)
}

const onCreateOrder = async () => {
  const amt = resolveAmount()
  if (!amt || amt <= 0) return AMessage.warning('请选择或输入有效金额')
  if (!userId.value) await userStore.getUserInfo()
  creatingOrder.value = true
  try {
    if (payMethod.value === 'wechat') {
      qrcodeUrl.value = new URL('@/assets/img/qrcode_xiaoai.webp', import.meta.url).href
    } else {
      const res = await financeStore.createRecharge({
        user_id: userId.value,
        amount: amt,
        payment_method: payMethod.value
      })
      currentOrderId.value = res.data.order_id
      qrcodeUrl.value = res.data.qr_code
    }
    qrcodeVisible.value = true
  } catch (e) {
    AMessage.error(e?.message || '创建充值订单失败')
  } finally {
    creatingOrder.value = false
  }
}

const onPaidCheck = async () => {
  if (!currentOrderId.value) return
  try {
    const ok = await financeStore.pollRechargeStatus({
      orderId: currentOrderId.value
    })
    qrcodeVisible.value = false
    if (ok) {
      AMessage.success('支付成功，请前往账单明细查看')
    } else {
      AMessage.warning('支付状态未确认，请稍后前往账单明细查看')
    }
    await Promise.all([
      financeStore.fetchBalance(userId.value, true),
      financeStore.fetchFlowList(userId.value, true),
      financeStore.fetchRechargeList(userId.value, true)
    ])
  } catch (e) {
    qrcodeVisible.value = false
    AMessage.error(e?.message || '支付状态未确认，请稍后前往账单明细查看')
  }
}

const onQrcodeCancel = () => {
  financeStore.cancelPolling()
}

onUnmounted(() => {
  // 组件卸载时确保取消轮询
  if (financeStore.polling) {
    financeStore.cancelPolling()
  }
})

// 列表与分页
const activeTab = ref('recharge')

const rechargeColumns = [
  {
    title: '订单号',
    dataIndex: 'order_id',
    width: 200,
    render: ({ record }) => {
      return h(
        'span',
        {
          class: `px-2 py-1 bg-blue-50 text-blue-500 rounded-full cursor-pointer`
        },
        record.order_id
      )
    }
  },
  {
    title: '金额',
    dataIndex: 'amount',
    width: 200,
    render: ({ record }) => `¥${formatMoney(record.amount)}`
  },
  {
    title: '支付方式',
    dataIndex: 'payment_method',
    width: 120,
    render: ({ record }) => {
      switch (record.payment_method) {
        case 'wechat':
          return '微信'
        case 'alipay':
          return '支付宝'
        default:
          return record.payment_method || '-'
      }
    }
  },
  {
    title: '支付状态',
    dataIndex: 'is_paid',
    width: 120,
    render: ({ record }) => {
      const text = record.is_paid ? '已支付' : '待支付'
      const bgColor = record.is_paid ? 'bg-green-50' : 'bg-orange-50'
      const textColor = record.is_paid ? 'text-green-500' : 'text-orange-500'
      return h(
        'span',
        {
          class: `px-2 py-1 ${bgColor} ${textColor} rounded-full cursor-pointer`
        },
        text
      )
    }
  },
  {
    title: '创建时间',
    dataIndex: 'create_at',
    width: 180,
    render: ({ record }) => formatDateTime(record.create_at)
  }
]

const flowColumns = [
  {
    title: '类型',
    dataIndex: 'change_type',
    width: 120,
    render: ({ record }) => {
      return h(
        'span',
        {
          class: `px-2 py-1 bg-blue-50 text-blue-500 rounded-full cursor-pointer`
        },
        mapChangeType(record.change_type)
      )
    }
  },
  {
    title: '金额变动',
    dataIndex: 'change',
    width: 140,
    render: ({ record }) => {
      const val = Number(record.change)
      const color = val >= 0 ? 'text-green-600' : 'text-red-600'
      const sign = val >= 0 ? '+' : ''
      return h('span', { class: color }, `${sign}¥${formatMoney(val)}`)
    }
  },
  {
    title: '时间',
    dataIndex: 'create_at',
    width: 180,
    render: ({ record }) => formatDateTime(record.create_at)
  }
]

const mapChangeType = t => {
  switch (t) {
    case 'recharge':
      return '充值入账'
    case 'invitation':
      return '邀请赠金'
    case 'redeem':
      return '兑换赠金'
    case 'order':
      return '订单消费'
    default:
      return t
  }
}

const refreshAll = async () => {
  try {
    await Promise.all([
      financeStore.fetchBalance(userId.value, true),
      financeStore.fetchRechargeList(userId.value, true),
      financeStore.fetchFlowList(userId.value, true)
    ])
    AMessage.success('已刷新')
  } catch (e) {
    console.error(e)
    AMessage.error('刷新失败')
  }
}

// 分页处理函数
const handleRechargePageChange = current => {
  financeStore.rechargePage.current = current
  financeStore.fetchRechargeList(userId.value, true)
}

const handleRechargePageSizeChange = pageSize => {
  financeStore.rechargePage.current = 1 // 重置到第一页
  financeStore.rechargePage.pageSize = pageSize
  financeStore.fetchRechargeList(userId.value, true)
}

const handleFlowPageChange = current => {
  financeStore.flowPage.current = current
  financeStore.fetchFlowList(userId.value, true)
}

const handleFlowPageSizeChange = pageSize => {
  financeStore.flowPage.current = 1 // 重置到第一页
  financeStore.flowPage.pageSize = pageSize
  financeStore.fetchFlowList(userId.value, true)
}
</script>

<style scoped>
:deep(.arco-card-header) {
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-neutral-3);
}

:deep(.arco-card-body) {
  padding: 0;
}

:deep(.arco-table-td) {
  text-align: center;
}

:deep(.arco-table-th .arco-table-cell) {
  justify-content: center;
  font-weight: bold;
}

:deep(.arco-checkbox-label) {
  font-size: 12px;
  color: var(--color-neutral-4);
}
</style>
