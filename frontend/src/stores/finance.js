import api from '@/api'
import { getConfig } from '@/config/index'

export const useFinanceStore = defineStore('finance', {
  state: () => ({
    // 余额统计
    balance: {
      total: 0,
      recharge: 0,
      gift: 0,
      consume: 0
    },
    // 充值记录
    rechargeList: [],
    rechargePage: { current: 1, pageSize: 10, total: 0 },
    // 流水
    flowList: [],
    flowPage: { current: 1, pageSize: 10, total: 0 },

    // 轮询状态
    polling: false,
    lastFetchTime: null,
    loading: false,
    cacheExpiry: 10 * 60 * 1000 // 10 分钟缓存
  }),

  getters: {
    isCacheExpired: state => {
      if (!state.lastFetchTime) return true
      return Date.now() - state.lastFetchTime > state.cacheExpiry
    }
  },

  actions: {
    reset() {
      this.balance = { total: 0, recharge: 0, gift: 0, consume: 0 }
      this.rechargeList = []
      this.flowList = []
      this.rechargePage = { current: 1, pageSize: 10, total: 0 }
      this.flowPage = { current: 1, pageSize: 10, total: 0 }
      this.lastFetchTime = null
      this.loading = false
      this.polling = false
    },

    async fetchBalance(userId, force = false) {
      if (!userId) {
        this.balance = { total: 0, recharge: 0, gift: 0, consume: 0 }
        return this.balance
      }
      if (!force && !this.isCacheExpired && this.balance && this.balance.total !== null) {
        return this.balance
      }
      const res = await api.getFinanceBalance({ user_id: userId })
      this.balance = {
        total: Number(res?.data?.total ?? res?.total ?? 0),
        recharge: Number(res?.data?.recharge ?? res?.recharge ?? 0),
        gift: Number(res?.data?.gift ?? res?.gift ?? 0),
        consume: Number(res?.data?.consume ?? res?.consume ?? 0)
      }
      this.lastFetchTime = Date.now()
      return this.balance
    },

    async fetchRechargeList(userId, force = false) {
      if (!force && !this.isCacheExpired && this.rechargeList.length > 0) {
        return this.rechargeList
      }
      this.loading = true
      try {
        const res = await api.getRechargeList({
          user_id: userId || '',
          page: this.rechargePage.current,
          page_size: this.rechargePage.pageSize
        })
        const data = res?.data || []
        this.rechargeList = Array.isArray(data) ? data : []
        this.rechargePage.total = res?.total || 0
        return this.rechargeList
      } finally {
        this.loading = false
      }
    },

    async fetchFlowList(userId, force = false) {
      if (!force && !this.isCacheExpired && this.flowList.length > 0) {
        return this.flowList
      }
      this.loading = true
      try {
        const res = await api.getFinanceBalanceList({
          user_id: userId || '',
          page: this.flowPage.current,
          page_size: this.flowPage.pageSize
        })
        const data = res?.data || []
        this.flowList = Array.isArray(data) ? data : []
        this.flowPage.total = res?.total || 0
        return this.flowList
      } finally {
        this.loading = false
      }
    },

    // 兑换码充值（会给 BalanceFlow 新增一条记录）
    async redeemCode({ userId, code }) {
      const res = await api.updateRedeem({
        code,
        redeem_id: userId,
        is_used: true
      })
      return res
    },

    // 创建充值订单（后端返回 order_id，等待 is_paid=false）
    async createRecharge(data) {
      try {
        const res = await api.createRecharge(data)
        this.rechargeList.unshift(res?.data)
        return res
      } catch (error) {
        console.error(error)
        throw error
      }
    },

    // 轮询检查是否已支付（后端应在支付回调时将 is_paid=true）
    async pollRechargeStatus({ orderId, intervalMs = 3000, maxTimes = 10 }) {
      this.polling = true
      try {
        for (let i = 0; i < maxTimes; i++) {
          const res = await api.getRechargeStatus({ order_id: orderId })
          const rec = res?.data?.is_paid
          if (rec) return true
          // 检查是否应该中断轮询
          if (!this.polling) return false
          await new Promise(r => setTimeout(r, intervalMs))
        }
        return false
      } catch (error) {
        console.error(error)
        throw error
      } finally {
        this.polling = false
      }
    },
    // 取消轮询
    cancelPolling() {
      this.polling = false
    }
  },

  persist: {
    key: `${getConfig('appCode')}-finance`,
    storage: localStorage,
    pick: ['balance', 'rechargeList', 'flowList', 'rechargePage', 'flowPage', 'lastFetchTime']
  }
})
