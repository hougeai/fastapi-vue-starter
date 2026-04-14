import api from '@/api'
import { getConfig } from '@/config/index'
import { formatMoney } from '@/utils'

export const useInviteStore = defineStore('invite', {
  state: () => ({
    stats: {
      invited_users: 0,
      valid_users: 0,
      total_reward: 0
    },
    list: [],
    lastFetchTime: null,
    loading: false,
    // 缓存有效期：60分钟
    cacheExpiry: 60 * 60 * 1000
  }),

  getters: {
    isCacheExpired: state => {
      if (!state.lastFetchTime) return true
      return Date.now() - state.lastFetchTime > state.cacheExpiry
    }
  },

  actions: {
    // 从列表聚合统计
    computeStats() {
      const invited_users = this.list.length
      let valid_users = 0
      let total_reward = 0
      for (const item of this.list) {
        if (item.status === 'rewarded') {
          valid_users += 1
          const amt = Number(item.amount ?? 0)
          if (!Number.isNaN(amt)) total_reward += amt
        }
      }
      this.stats = {
        invited_users,
        valid_users,
        total_reward: formatMoney(total_reward)
      }
    },

    // 获取邀请列表（智能缓存）
    async fetchInviteList(userId, forceRefresh = false) {
      if (!userId) {
        this.list = []
        this.computeStats()
        return this.list
      }
      if (!forceRefresh && this.list.length > 0 && !this.isCacheExpired) {
        return this.list
      }
      try {
        this.loading = true
        const res = await api.getInvitationList({
          inviter_id: userId,
          page: 1,
          page_size: 999
        })
        const data = res?.data || []
        this.list = Array.isArray(data) ? data : []
        this.lastFetchTime = Date.now()
        this.computeStats()
        return this.list
      } catch (error) {
        console.error('获取邀请列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async refreshInviteList(userId) {
      return this.fetchInviteList(userId, true)
    },

    reset() {
      this.stats = { invited_users: 0, valid_users: 0, total_reward: 0 }
      this.list = []
      this.lastFetchTime = null
      this.loading = false
    }
  },

  persist: {
    key: `${getConfig('appCode')}-invite`,
    storage: localStorage,
    pick: ['stats', 'list', 'lastFetchTime']
  }
})
