<script setup>
import { useRoomStore } from '@/stores/room'
import { getConfig, getLanguageLabel, getPlatformLabel } from '@/config/index'
import { formatDate } from '@/utils/common'
import { useRouter } from 'vue-router'

const roomStore = useRoomStore()
const router = useRouter()

// 计算属性
const rooms = computed(() => roomStore.rooms)

// 获取直播间数据
onMounted(async () => {
  try {
    await roomStore.fetchRooms()
  } catch (error) {
    console.error('获取直播间数据失败:', error)
  }
})

// 刷新数据
const refreshData = async () => {
  try {
    await roomStore.refreshRooms()
  } catch (error) {
    console.error('刷新直播间数据失败:', error)
  }
}

// 筛选后的直播间列表
const roomStatus = ref('all')
const filteredRooms = computed(() => {
  if (roomStatus.value === 'all') {
    return rooms.value
  } else {
    return rooms.value.filter(room => {
      return room.status === roomStatus.value
    })
  }
})

// 创建新直播间
const createNewroom = () => {
  router.push('/dashboard/live-room/create')
}

// 编辑直播间
const editRoom = room => {
  router.push(`/dashboard/live-room/edit/${room.id}`)
}

// 删除直播间
const deleteRoom = async roomId => {
  AModal.confirm({
    title: '删除直播间',
    content: '确定要删除当前直播间吗？此操作不可恢复。',
    okText: '删除',
    cancelText: '取消',
    okButtonProps: { status: 'danger' },
    onOk: async () => {
      await roomStore.deleteRoom(roomId)
    }
  })
}
</script>

<template>
  <!-- 顶部操作区 -->
  <router-view v-if="$route.meta.hideParentContent" />
  <div v-else class="w-full p-6 bg-[var(--color-fill-0)]">
    <!-- 顶部操作区 -->
    <div class="flex flex-wrap items-center mb-6 px-6 space-x-4">
      <a-radio-group v-model="roomStatus" type="button">
        <a-radio value="all">全部直播间</a-radio>
        <a-radio value="online">已开播</a-radio>
        <a-radio value="offline">未开播</a-radio>
      </a-radio-group>

      <a-button type="primary" size="large" style="border-radius: 0.5rem" @click="createNewroom">
        <template #icon><icon-ri-add-circle-line /></template>
        新建直播间
      </a-button>

      <a-button
        type="outline"
        size="large"
        shape="round"
        :loading="roomStore.loading"
        @click="refreshData"
      >
        <template #icon>
          <icon-material-symbols:refresh />
        </template>
        刷新
      </a-button>
    </div>

    <!-- 直播间列表 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 px-6">
      <div
        v-for="room in filteredRooms"
        :key="room.id"
        class="flex-shrink-0 border rounded-lg overflow-hidden shadow-md hover:shadow-xl bg-gradient-to-br from-blue-50 to-purple-50/30 bg-blue-200 transition-all duration-300"
      >
        <div class="p-4 flex items-center gap-4">
          <div class="flex-shrink-0">
            <img
              :src="
                room.host_agent?.avatar
                  ? `${getConfig('ossUrl')}/${room.host_agent.avatar}`
                  : getConfig('me.avatar')
              "
              alt="avatar"
              class="w-16 h-16 rounded-full object-cover"
            />
          </div>

          <div class="flex-1 flex flex-col justify-center space-y-1">
            <div class="flex items-center">
              <div class="font-bold text-lg truncate mr-2">{{ room.name }}</div>
              <a-tag size="small" color="orange">
                {{ getLanguageLabel(room.host_agent?.lang) }}
              </a-tag>
            </div>

            <div class="flex flex-wrap gap-1">
              <span
                v-for="tag in room.tags?.split('|')"
                :key="tag"
                class="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full truncate"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <!-- 卡片信息 -->
        <div class="grid grid-cols-3 gap-2 text-center text-sm px-2">
          <div class="bg-[var(--color-fill-2)] rounded-lg shadow-sm py-3">
            <div class="text-[var(--color-text-3)]">累计直播</div>
            <div>{{ room.live_times }}</div>
          </div>
          <div class="bg-[var(--color-fill-2)] rounded-lg shadow-sm py-3">
            <div class="text-[var(--color-text-3)]">最近直播</div>
            <div>{{ room.last_active ? formatDate(room.last_active) : '-' }}</div>
          </div>
          <div class="bg-[var(--color-fill-2)] rounded-lg shadow-sm py-3">
            <div class="text-[var(--color-text-3)]">直播平台</div>
            <div>{{ getPlatformLabel(room.platform) }}</div>
          </div>
        </div>

        <div class="px-4 py-3 flex justify-between gap-2">
          <!-- 新增左侧创建时间 -->
          <div class="text-sm text-gray-600 flex items-center">创建时间: {{ room.create_at }}</div>

          <!-- 右侧操作按钮 -->
          <div class="flex gap-2">
            <a-tooltip content="打开控制台">
              <a-button type="text" size="small" shape="circle" @click="editRoom(room)">
                <template #icon><icon-mdi:console /></template>
              </a-button>
            </a-tooltip>
            <a-tooltip content="删除直播间">
              <a-button
                type="text"
                size="small"
                status="danger"
                shape="circle"
                :loading="roomStatus.loadingDelete"
                @click="deleteRoom(room.id)"
              >
                <template #icon><icon-material-symbols:delete-outline /></template>
              </a-button>
            </a-tooltip>
          </div>
        </div>
      </div>
    </div>
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
