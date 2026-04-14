<template>
  <div class="w-full h-full flex flex-col">
    <!-- 顶部操作栏 -->
    <div class="flex items-center gap-3 m-4">
      <a-popover
        trigger="click"
        v-model:popup-visible="copyVisible"
        position="bottom"
        :arrow="false"
      >
        <a-button type="primary" size="large" style="border-radius: 0.5rem">
          👉复制邀请链接
        </a-button>
        <template #content>
          <div class="flex items-center gap-2">
            <a-input :model-value="inviteLink" :style="inputAutoWidthStyle" readonly />
            <a-button type="text" @click="copyInviteLink" :shape="'circle'">
              <template #icon>
                <icon-material-symbols:content-copy />
              </template>
            </a-button>
          </div>
        </template>
      </a-popover>

      <a-button type="outline" size="large" shape="round" :loading="loading" @click="refreshAll">
        <template #icon>
          <icon-material-symbols:refresh />
        </template>
        刷新
      </a-button>
    </div>

    <!-- 两个卡片：奖励说明 & 奖励统计 -->
    <div class="mx-4 mb-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- 奖励说明 -->
      <div
        class="bg-gradient-to-br from-blue-50 to-purple-50/30 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden p-4"
      >
        <div class="flex items-start gap-3">
          <div class="flex-1">
            <div class="text-lg font-semibold mb-2">奖励说明</div>
            <div class="space-y-2">
              <div class="flex items-start gap-2 p-2 rounded-lg bg-gray-50">
                <icon-material-symbols:check-circle class="text-green-500 mt-0.5" />
                <div class="text-gray-700">
                  邀请好友，注册并<span class="font-bold">充值</span>，双方均可获得相应奖励
                </div>
              </div>
              <div class="flex items-start gap-2 p-2 rounded-lg bg-gray-50">
                <icon-material-symbols:savings class="text-amber-500 mt-0.5" />
                <div class="text-gray-700">
                  奖励实时到账，永不过期，仅限于{{ getConfig('projectName') }}平台使用
                </div>
              </div>
              <div class="flex items-start gap-2 p-2 rounded-lg bg-gray-50">
                <icon-material-symbols:report class="text-red-500 mt-0.5" />
                <div class="text-gray-700">
                  严禁奖励转卖、刷单等违规行为，平台将对违反规则的账户取消奖励资格并追究相关责任
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 奖励统计 -->
      <div
        class="bg-gradient-to-br from-blue-50 to-purple-50/30 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden p-4"
      >
        <div class="flex items-center justify-between mb-6">
          <div class="text-lg font-semibold">奖励统计</div>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div
            class="rounded-xl p-3 text-center"
            style="
              background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
              border: 1px solid var(--color-neutral-3);
            "
          >
            <div class="flex items-center justify-center gap-1 text-gray-500 text-xs mb-1">
              <icon-material-symbols:group class="text-blue-600" />
              邀请用户
            </div>
            <div class="text-2xl font-extrabold text-gray-900 leading-none">
              {{ stats.invited_users }}
            </div>
          </div>

          <div
            class="rounded-xl p-3 text-center"
            style="
              background: linear-gradient(180deg, #f7fffb 0%, #ffffff 100%);
              border: 1px solid var(--color-neutral-3);
            "
          >
            <div class="flex items-center justify-center gap-1 text-gray-500 text-xs mb-1">
              <icon-material-symbols:verified class="text-emerald-600" />
              有效用户
            </div>
            <div class="text-2xl font-extrabold text-gray-900 leading-none">
              {{ stats.valid_users }}
            </div>
          </div>

          <div
            class="rounded-xl p-3 text-center"
            style="
              background: linear-gradient(180deg, #fff9f2 0%, #ffffff 100%);
              border: 1px solid var(--color-neutral-3);
            "
          >
            <div class="flex items-center justify-center gap-1 text-gray-500 text-xs mb-1">
              <icon-material-symbols:paid class="text-amber-600" />
              总收益
            </div>
            <div class="text-2xl font-extrabold text-gray-900 leading-none">
              ¥{{ formatMoney(stats.total_reward) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 邀请列表表格 -->
    <div class="flex-1 mx-4 mb-4">
      <a-card class="h-full w-full">
        <template #title>
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold">邀请列表</span>
            <span class="text-sm text-gray-500"> 共 {{ list.length }} 条 </span>
          </div>
        </template>

        <a-table
          :columns="columns"
          :data="paginatedList"
          :loading="loading"
          :bordered="true"
          :stripe="true"
          :pagination="false"
          row-key="invitee_id"
          size="large"
        >
          <template #empty>
            <div class="text-center py-8">
              <div class="text-6xl text-gray-300 mb-4">
                <icon-material-symbols:group-add />
              </div>
              <div class="text-gray-500">暂无邀请记录</div>
            </div>
          </template>
        </a-table>

        <!-- 分页 -->
        <div class="flex justify-center mt-4" v-if="list.length > 0">
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

<script setup>
import { reactive, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useInviteStore } from '@/stores/invite'
import { formatDateTime, maskKey, formatMoney } from '@/utils'
import { getConfig } from '@/config'

const userStore = useUserStore()
const inviteStore = useInviteStore()

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showTotal: true,
  showPageSize: true
})

const loading = computed(() => inviteStore.loading)
const stats = computed(() => inviteStore.stats)
const list = computed(() => inviteStore.list)
const userId = computed(() => userStore.userId)

// 邀请链接：用 inviter_id（当前用户ID）编码到 URL
const inviteLink = computed(() => {
  const base = window.location.origin
  const code = userId.value ? encodeURIComponent(userId.value) : ''
  return `${base}/?i=${code}`
})

watch(
  list,
  val => {
    pagination.total = val?.length || 0
  },
  { immediate: true }
)

onMounted(async () => {
  try {
    if (!userId.value) {
      await userStore.getUserInfo()
    }
    await inviteStore.fetchInviteList(userId.value)
  } catch (e) {
    console.error('邀请页初始化失败:', e)
    AMessage.error('页面初始化失败')
  }
})

const refreshAll = async () => {
  try {
    await inviteStore.refreshInviteList(userId.value)
    AMessage.success('已刷新')
  } catch (e) {
    console.error(e)
    AMessage.error('刷新失败')
  }
}

const copyVisible = ref(false)
const copyInviteLink = async () => {
  try {
    await navigator.clipboard.writeText(inviteLink.value)
    AMessage.success('邀请链接已复制')
    copyVisible.value = false
  } catch {
    AMessage.error('复制失败')
  }
}

const columns = [
  {
    title: '受邀人ID',
    dataIndex: 'invitee_id',
    width: 180,
    render: ({ record }) => {
      return h(
        'span',
        {
          class: `px-2 py-1 bg-blue-50 text-blue-500 rounded-full cursor-pointer`
        },
        maskKey(record.invitee_id)
      )
    }
  },
  {
    title: '注册时间',
    dataIndex: 'create_at',
    width: 200,
    render: ({ record }) => (record.update_at ? formatDateTime(record.create_at) : '—')
  },
  {
    title: '邀请状态',
    dataIndex: 'status',
    width: 140,
    render: ({ record }) => {
      const text = record.status === 'pending' ? '待生效' : '已生效'
      const bgColor = record.status === 'pending' ? 'bg-orange-50' : 'bg-green-50'
      const textColor = record.status === 'pending' ? 'text-orange-500' : 'text-green-500'
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
    title: '生效时间',
    dataIndex: 'update_at',
    width: 200,
    render: ({ record }) => (record.status === 'rewarded' ? formatDateTime(record.update_at) : '—')
  },
  {
    title: '奖励金额',
    dataIndex: 'amount',
    width: 140,
    render: ({ record }) => (record.status === 'rewarded' ? `¥${formatMoney(record.amount)}` : '—')
  }
]

const paginatedList = computed(() => {
  const start = (pagination.current - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return list.value.slice(start, end)
})

const onPageChange = current => {
  pagination.current = current
}

const onPageSizeChange = size => {
  pagination.pageSize = size
  pagination.current = 1
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
</style>
