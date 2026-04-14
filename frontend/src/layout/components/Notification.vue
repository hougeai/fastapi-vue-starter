<script setup>
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

// 获取响应式的 notifications（通知列表）和 unreadCount（未读通知数量）
const { notifications, unreadCount } = storeToRefs(notificationStore)

onMounted(() => {
  notificationStore.initNotifications()
})

// 处理通知点击：标记已读
const handleNotificationClick = async notification => {
  if (!notification.is_read) {
    try {
      await notificationStore.markAsRead(notification.id)
    } catch (error) {
      console.error(error)
      AMessage.error('标记已读失败')
    }
  }
}

// 删除通知
const handleDeleteNotification = async (e, id) => {
  e.stopPropagation()
  try {
    await notificationStore.deleteNotification(id)
    AMessage.success('通知已删除')
  } catch (error) {
    console.error(error)
    AMessage.error('删除失败')
  }
}

// 标记全部已读
const handleMarkAllRead = async () => {
  try {
    await notificationStore.markAllAsRead()
    AMessage.success('已标记全部为已读')
  } catch (error) {
    console.error(error)
    AMessage.error('操作失败')
  }
}

// 清空所有通知
const handleClearAll = () => {
  AModal.confirm({
    title: '确认清空',
    content: '确定要清空所有通知吗？此操作不可撤销。',
    okText: '确认清空',
    cancelText: '取消',
    onOk: async () => {
      try {
        await notificationStore.clearAllNotifications()
        AMessage.success('已清空所有通知')
      } catch (error) {
        console.error(error)
        AMessage.error('清空失败')
      }
    }
  })
}
</script>

<template>
  <a-dropdown trigger="hover" :popup-max-height="false" position="br">
    <a-button type="text">
      <template #icon>
        <a-badge :count="unreadCount" :max-count="99" :offset="[2, -2]">
          <icon-material-symbols:circle-notifications-sharp
            class="text-[var(--color-text-1)] text-18px"
          />
        </a-badge>
      </template>
    </a-button>

    <template #content>
      <div class="w-350px max-h-500px">
        <!-- 头部 -->
        <div
          class="px-4 py-3 border-b border-[var(--color-border-2)] flex items-center justify-between"
        >
          <div class="flex items-center">
            <icon-material-symbols:circle-notifications-sharp class="text-lg mr-2" />
            <span class="font-bold">通知中心</span>
            <a-badge v-if="unreadCount > 0" :count="unreadCount" :max-count="99" class="ml-2" />
          </div>
          <div class="flex items-center space-x-2">
            <a-button
              v-if="unreadCount > 0"
              type="text"
              size="mini"
              @click="handleMarkAllRead"
              class="text-xs"
            >
              全部已读
            </a-button>
            <a-button
              v-if="notifications.length > 0"
              type="text"
              size="mini"
              @click="handleClearAll"
              class="text-xs text-red-500"
            >
              清空
            </a-button>
          </div>
        </div>

        <!-- 通知列表 -->
        <div class="max-h-400px overflow-y-auto">
          <div v-if="notifications.length === 0" class="px-4 py-4 text-center text-gray-500">
            <icon-material-symbols:notifications-off-sharp class="text-4xl mb-2 mx-auto block" />
            <div>暂无通知</div>
          </div>

          <div v-else>
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="px-4 hover:bg-[var(--color-fill-1)] cursor-pointer transition-colors relative group"
              :class="{ 'bg-[var(--color-primary-light-1)]': !notification.is_read }"
              @click="handleNotificationClick(notification)"
            >
              <!-- 未读指示器 -->
              <div
                v-if="!notification.is_read"
                class="absolute left-2 top-1/2 transform -translate-y-1/2 w-2 h-2 bg-red-500 rounded-full"
              ></div>

              <div class="flex items-start space-x-3" :class="{ 'ml-3': !notification.is_read }">
                <!-- 通知内容 -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-1">
                      <icon-material-symbols:system-update-alt
                        v-if="notification.type === 'system'"
                        class="text-lg text-[var(--color-primary-light-4)]"
                      />
                      <icon-material-symbols:person-alert
                        v-else-if="notification.type === 'personal'"
                        class="text-lg text-[var(--color-warning-light-4)]"
                      />
                      <h4 class="font-semibold text-sm truncate leading-tight">
                        {{ notification.title }}
                      </h4>
                    </div>
                    <div
                      class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <a-button
                        type="text"
                        size="mini"
                        @click="handleDeleteNotification($event, notification.id)"
                        class="text-red-500 hover:bg-red-50"
                      >
                        <template #icon>
                          <icon-material-symbols:delete-outline class="text-sm" />
                        </template>
                      </a-button>
                    </div>
                  </div>
                  <p class="text-xs text-gray-600 mt-0.5 line-clamp-2">
                    {{ notification.content }}
                  </p>
                  <div class="text-xs text-gray-400 mt-1">
                    {{ notificationStore.formatTime(notification.time) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- TODO 底部操作：点击后跳转通知中心页面 or 模态框  -->
        <div
          v-if="notifications.length > 0"
          class="px-4 py-3 border-t border-[var(--color-border-2)] text-center"
        >
          <a-button type="text" size="small" class="text-[var(--color-primary-6)]">
            查看全部通知
          </a-button>
        </div>
      </div>
    </template>
  </a-dropdown>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 自定义滚动条 */
.max-h-400px::-webkit-scrollbar {
  width: 4px;
}

.max-h-400px::-webkit-scrollbar-track {
  background: var(--color-fill-2);
}

.max-h-400px::-webkit-scrollbar-thumb {
  background: var(--color-fill-4);
  border-radius: 2px;
}

.max-h-400px::-webkit-scrollbar-thumb:hover {
  background: var(--color-fill-3);
}
</style>
