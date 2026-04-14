<script setup>
import { useHostStore } from '@/stores/host'
import { getConfig, getLanguageLabel } from '@/config/index'
import { formatDate, formatDuration } from '@/utils/common'
const hostStore = useHostStore()
// 计算属性
const hosts = computed(() => hostStore.hosts)

// 创建新主播对话框
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const currentHost = ref({})

// 搜索与筛选
const languageOptions = getConfig('languageOptions')
const selectedLanguage = ref('全部语言')
const searchQuery = ref('')

// 获取主播数据
onMounted(async () => {
  try {
    await hostStore.fetchHosts()
  } catch (error) {
    console.error('获取主播数据失败:', error)
  }
})

// 刷新数据
const refreshData = async () => {
  try {
    await hostStore.refreshHosts()
  } catch (error) {
    console.error('刷新主播数据失败:', error)
  }
}

// 筛选后的主播列表
const filteredHosts = computed(() => {
  return hosts.value.filter(host => {
    const matchesLanguage =
      selectedLanguage.value === '全部语言' || host.lang === selectedLanguage.value
    const matchesSearch =
      host.name.includes(searchQuery.value) || host.lang.includes(searchQuery.value)
    return matchesLanguage && matchesSearch
  })
})

// 创建新主播
const createNewHost = () => {
  showCreateDialog.value = true
}

// 编辑主播
const editHost = host => {
  currentHost.value = host
  showEditDialog.value = true
}

// 删除主播
const deleteHost = async hostId => {
  AModal.confirm({
    title: '删除主播',
    content: '确定要删除当前主播吗？此操作不可恢复。',
    okText: '删除',
    cancelText: '取消',
    okButtonProps: { status: 'danger' },
    onOk: async () => {
      await hostStore.deleteHost(hostId)
    }
  })
}
</script>

<template>
  <div class="w-full p-6 bg-[var(--color-fill-0)]">
    <!-- 顶部操作区 -->
    <div class="flex flex-wrap items-center mb-6 px-6 space-x-4">
      <a-select
        v-model="selectedLanguage"
        :options="languageOptions"
        style="width: 120px"
        size="large"
      />

      <a-input-search
        v-model="searchQuery"
        placeholder="请输入主播名称检索"
        style="flex: 1; max-width: 200px"
        size="large"
      />

      <a-button type="primary" size="large" style="border-radius: 0.5rem" @click="createNewHost">
        <template #icon><icon-ri-add-circle-line /></template>
        创建新主播
      </a-button>

      <a-button
        type="outline"
        size="large"
        shape="round"
        :loading="hostStore.loading"
        @click="refreshData"
      >
        <template #icon>
          <icon-material-symbols:refresh />
        </template>
        刷新
      </a-button>
    </div>

    <!-- 主播列表 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 px-6">
      <div
        v-for="host in filteredHosts"
        :key="host.id"
        class="flex-shrink-0 border rounded-lg overflow-hidden shadow-md hover:shadow-xl bg-gradient-to-br from-blue-50 to-purple-50/30 bg-blue-200 transition-all duration-300"
      >
        <div class="p-4 flex items-center gap-4">
          <div class="flex-shrink-0">
            <img
              :src="host.avatar ? `${getConfig('ossUrl')}/${host.avatar}` : getConfig('me.avatar')"
              alt="avatar"
              class="w-16 h-16 rounded-full object-cover"
            />
          </div>

          <div class="flex-1 flex flex-col justify-center space-y-1">
            <div class="flex items-center">
              <div class="font-bold text-lg truncate mr-2">{{ host.name }}</div>
              <a-tag size="small" color="orange">
                {{ getLanguageLabel(host.lang) }}
              </a-tag>
            </div>

            <div class="flex flex-wrap gap-1">
              <span
                v-for="tag in host.tags?.split('|')"
                :key="tag"
                class="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full truncate"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <!-- 卡片信息（累计直播、最近直播、长期记忆） -->
        <div class="grid grid-cols-3 gap-2 text-center text-sm px-2">
          <div class="bg-[var(--color-fill-2)] rounded-lg shadow-sm py-3">
            <div class="text-[var(--color-text-3)]">累计直播</div>
            <div>{{ formatDuration(host.duration_sum) }}</div>
          </div>
          <div class="bg-[var(--color-fill-2)] rounded-lg shadow-sm py-3">
            <div class="text-[var(--color-text-3)]">最近直播</div>
            <div>{{ host.last_active ? formatDate(host.last_active) : '-' }}</div>
          </div>
          <div class="bg-[var(--color-fill-2)] rounded-lg shadow-sm py-3">
            <div class="text-[var(--color-text-3)]">长期记忆</div>
            <div>{{ host.mem_num }} 条</div>
          </div>
        </div>

        <div class="px-4 py-3 flex justify-between gap-2">
          <!-- 新增左侧创建时间 -->
          <div class="text-sm text-gray-600 flex items-center">创建时间: {{ host.create_at }}</div>

          <!-- 右侧操作按钮 -->
          <div class="flex gap-2">
            <a-tooltip content="编辑主播">
              <a-button type="text" size="small" shape="circle" @click="editHost(host)">
                <template #icon><icon-ri-user-line /></template>
              </a-button>
            </a-tooltip>
            <a-tooltip content="删除主播">
              <a-button
                type="text"
                size="small"
                status="danger"
                shape="circle"
                @click="deleteHost(host.id)"
              >
                <template #icon><icon-material-symbols:delete-outline /></template>
              </a-button>
            </a-tooltip>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建主播对话框 -->
    <HostCreateDialog
      v-model:visible="showCreateDialog"
      mode="create"
      :language-options="languageOptions.filter(opt => opt.value !== '全部语言')"
    />

    <!-- 编辑主播对话框 -->
    <HostCreateDialog
      v-model:visible="showEditDialog"
      mode="edit"
      :host-data="currentHost"
      :language-options="languageOptions.filter(opt => opt.value !== '全部语言')"
    />
  </div>
</template>

<style scoped>
/* 响应式优化 */
@media (max-width: 768px) {
  .grid-cols-4 {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
