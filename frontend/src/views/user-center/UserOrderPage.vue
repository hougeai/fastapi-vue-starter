<script setup>
import { reactive, computed, onMounted, watch, h } from 'vue'
import { useUserStore } from '@/stores/user'
import { useOrderStore } from '@/stores/order'
import { formatDateTime } from '@/utils'

const userStore = useUserStore()
const orderStore = useOrderStore()

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true,
  showPageSize: true
})

const orders = computed(() => orderStore.orders || [])
const loading = computed(() => orderStore.loading)
const userId = computed(() => userStore.userId)

const paginatedOrders = computed(() => {
  const start = (pagination.current - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return orders.value.slice(start, end)
})

watch(
  orders,
  list => {
    pagination.total = list?.length || 0
  },
  { immediate: true }
)

const refreshOrders = async () => {
  try {
    await orderStore.refreshOrders(userId.value)
    AMessage.success('订单已刷新')
  } catch (e) {
    console.error(e)
    AMessage.error('刷新失败')
  }
}

const onPageChange = current => {
  pagination.current = current
}
const onPageSizeChange = size => {
  pagination.pageSize = size
  pagination.current = 1
}

onMounted(async () => {
  try {
    if (!userId.value) {
      await userStore.getUserInfo()
    }
    await orderStore.fetchOrders(userId.value)
  } catch (e) {
    console.error('初始化失败:', e)
    AMessage.error('页面初始化失败')
  }
})

// 表格列（参考后端 UserOrder）
const columns = [
  { title: '创建时间', dataIndex: 'create_at', width: 180, ellipsis: true },
  {
    title: '订单内容',
    dataIndex: 'role_id',
    width: 100,
    render: ({ record }) => {
      const roleIdMap = {
        4: 'VIP会员',
        5: 'SVIP会员'
      }
      const text = roleIdMap[record.role_id] || record.role_id
      return h(
        'span',
        {
          class: 'px-2 py-1 bg-blue-50 text-blue-500 rounded-full cursor-pointer'
        },
        text
      )
    }
  },
  {
    title: '支付周期',
    dataIndex: 'payment_period',
    width: 120,
    render: ({ record }) => {
      const text = record.payment_period === 'monthly' ? '月付' : '年付'
      return h(
        'span',
        {
          class: `px-2 py-1 bg-blue-50 text-blue-500 rounded-full cursor-pointer`
        },
        text
      )
    }
  },
  {
    title: '到期时间',
    dataIndex: 'expire_at',
    width: 180,
    render: ({ record }) => (record.expire_at ? formatDateTime(record.expire_at) : '-')
  },
  {
    title: '到期状态',
    dataIndex: 'is_expired',
    width: 120,
    render: ({ record }) => {
      if (!record.expire_at) {
        return '-'
      }
      const text = record.is_expired ? '已过期' : '正常使用'
      const bgColor = record.is_expired ? 'bg-orange-50' : 'bg-green-50'
      const textColor = record.is_expired ? 'text-orange-500' : 'text-green-500'
      return h(
        'span',
        {
          class: `px-2 py-1 ${bgColor} ${textColor} rounded-full cursor-pointer`
        },
        text
      )
    }
  }
]
</script>

<template>
  <div class="w-full h-full flex flex-col">
    <!-- 顶部操作栏：左标题 右刷新 -->
    <div class="flex items-center justify-between m-4 gap-4">
      <h2 class="text-xl font-semibold">我的订单</h2>
      <a-button type="outline" size="large" shape="round" :loading="loading" @click="refreshOrders">
        <template #icon>
          <icon-material-symbols:refresh />
        </template>
        刷新
      </a-button>
    </div>

    <!-- 主体表格卡片 -->
    <div class="flex-1 mx-4 mb-4">
      <a-card class="h-full">
        <template #title>
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold">订单列表</span>
            <span class="text-sm text-gray-500">共 {{ orders.length }} 条</span>
          </div>
        </template>

        <a-table
          :columns="columns"
          :data="paginatedOrders"
          :loading="loading"
          :bordered="true"
          :stripe="true"
          :pagination="false"
          row-key="id"
          size="large"
        >
          <template #empty>
            <div class="text-center py-10">
              <div class="text-6xl text-gray-300 mb-3">
                <icon-material-symbols:assignment-outline />
              </div>
              <div class="text-gray-500">你还没有相关订单</div>
            </div>
          </template>
        </a-table>

        <div class="flex justify-center mt-4" v-if="orders.length > 0">
          <a-pagination
            v-model:current="pagination.current"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :show-total="pagination.showTotal"
            :show-page-size="pagination.showPageSize"
            @change="onPageChange"
            @page-size-change="onPageSizeChange"
          />
        </div>
      </a-card>
    </div>
  </div>
</template>

<style scoped>
:deep(.arco-card-header) {
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-neutral-3);
}

:deep(.arco-card-body) {
  padding: 0;
  height: calc(100% - 57px);
  overflow: hidden;
}

:deep(.arco-table-container) {
  height: calc(100% - 60px);
}

:deep(.arco-table-body) {
  max-height: none;
}

:deep(.arco-table-td) {
  text-align: center;
}

:deep(.arco-table-th .arco-table-cell) {
  justify-content: center;
  font-weight: bold;
}
</style>
