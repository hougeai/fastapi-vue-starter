import api from '@/api'
import { getConfig } from '@/config/index'

export const useOrderStore = defineStore('order', {
  state: () => ({
    orders: [],
    lastFetchTime: null,
    loading: false,
    // 缓存有效期：60分钟
    cacheExpiry: 60 * 60 * 1000
  }),

  getters: {
    // 检查缓存是否过期
    isCacheExpired: state => {
      if (!state.lastFetchTime) return true
      return Date.now() - state.lastFetchTime > state.cacheExpiry
    }
  },

  actions: {
    // 获取订单列表（智能缓存）
    async fetchOrders(userId, forceRefresh = false) {
      if (!userId) {
        this.orders = []
        return this.orders
      }

      // 如果有缓存且未过期，且不是强制刷新，直接返回
      if (!forceRefresh && this.orders.length > 0 && !this.isCacheExpired) {
        return this.orders
      }

      try {
        this.loading = true
        const response = await api.getOrderList({ user_id: userId, page: 1, page_size: 999 })
        // 过滤掉订单数据中的id字段
        this.orders =
          response?.data?.map(order => {
            const { ...orderWithoutId } = order
            return orderWithoutId
          }) || []
        this.lastFetchTime = Date.now()
        return this.orders
      } catch (error) {
        console.error('获取订单列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 创建订单
    async createOrder(orderData) {
      try {
        const res = await api.createOrder(orderData)
        // 如果订单创建成功，更新本地订单列表
        this.orders.unshift(res?.data)
      } catch (error) {
        console.error('创建订单失败:', error)
        throw error
      }
    },

    // 强制刷新订单列表
    async refreshOrders(userId) {
      return this.fetchOrders(userId, true)
    },

    // 清空订单缓存
    reset() {
      this.orders = []
      this.lastFetchTime = null
      this.loading = false
    }
  },

  // 持久化配置
  persist: {
    key: `${getConfig('appCode')}-order`,
    storage: localStorage,
    // 只持久化订单数据和最后获取时间
    pick: ['orders', 'lastFetchTime']
  }
})
