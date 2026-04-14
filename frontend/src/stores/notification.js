import api from '@/api'
import { getConfig } from '@/config/index'
import { useUserStore } from './user'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    notifications: [],
    lastRefreshDate: null // 按天刷新
  }),

  getters: {
    // 未读通知数量
    unreadCount: state => {
      return state.notifications.filter(n => !n.is_read).length
    }
  },

  actions: {
    async initNotifications() {
      // 检查用户是否登录
      const userStore = useUserStore()
      if (!userStore.userId) {
        return
      }
      // 检查是否需要刷新
      if (this.shouldRefresh()) {
        await this.fetchNotifications()
      }
    },
    // 获取通知列表
    async fetchNotifications() {
      try {
        this.loading = true
        const response = await api.fetchNotifications()
        this.notifications = response.data
        this.lastRefreshDate = new Date().toDateString()
      } catch (error) {
        console.error('获取通知列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 检查是否需要刷新（每天一次）
    shouldRefresh() {
      const today = new Date().toDateString()
      return this.lastRefreshDate !== today
    },

    // 标记单个通知为已读
    async markAsRead(notificationId) {
      try {
        // 调用 API 更新
        await api.markNotificationRead({ ids: [notificationId] })
        // 更新本地状态
        const notification = this.notifications.find(n => n.id === notificationId)
        if (notification) {
          notification.is_read = true
        }
        return true
      } catch (error) {
        console.error('标记通知已读失败:', error)
        throw error
      }
    },

    // 标记所有通知为已读
    async markAllAsRead() {
      if (this.unreadCount === 0) return true
      try {
        // 调用 API 批量更新
        await api.markNotificationRead({
          ids: this.notifications.filter(n => !n.is_read).map(n => n.id)
        })
        // 更新本地状态
        this.notifications.forEach(n => {
          n.is_read = true
        })
        return true
      } catch (error) {
        console.error('标记全部通知已读失败:', error)
        throw error
      }
    },

    // 删除通知
    async deleteNotification(notificationId) {
      try {
        // 调用 API 删除
        await api.deleteNotification({ ids: [notificationId] })
        this.notifications = this.notifications.filter(n => n.id !== notificationId)
        return true
      } catch (error) {
        console.error('删除通知失败:', error)
        throw error
      }
    },

    // 清空所有通知
    async clearAllNotifications() {
      try {
        if (this.notifications.length === 0) return true
        // 调用 API 清空
        await api.deleteNotification({ ids: this.notifications.map(n => n.id) })
        this.notifications = []
        return true
      } catch (error) {
        console.error('清空通知失败:', error)
        throw error
      }
    },

    // 格式化时间显示
    formatTime(time) {
      const now = new Date()
      const timeDate = new Date(time) // 先转换为 Date 对象
      const diff = now - timeDate
      const minutes = Math.floor(diff / (1000 * 60))
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))

      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 7) return `${days}天前`

      return timeDate.toLocaleDateString()
    },

    reset() {
      this.notifications = []
      this.lastRefreshDate = null
    }
  },

  // 持久化配置
  persist: {
    key: `${getConfig('appCode')}-notification`,
    storage: localStorage,
    // 只持久化通知数据和最后获取时间
    pick: ['notifications', 'lastRefreshDate']
  }
})
