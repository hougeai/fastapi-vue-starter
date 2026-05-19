import api from '@/api'
import { removeToken } from '@/utils'
import { getConfig } from '@/config/index'
import { router } from '@/router'
import { useLedgerStore } from './ledger'
import { useTransactionStore } from './transaction'

export const useUserStore = defineStore('user', {
  state() {
    return {
      userInfo: {},
      loading: false
    }
  },
  getters: {
    userId() {
      return this.userInfo?.user_id
    },
    userName() {
      return this.userInfo?.user_name || this.userInfo?.username
    },
    email() {
      return this.userInfo?.email
    },
    avatar() {
      return this.userInfo?.avatar || getConfig('me.avatar')
    }
  },
  actions: {
    // 获取用户信息
    async getUserInfo(forceRefresh = false) {
      if (!forceRefresh && Object.keys(this.userInfo).length > 0) {
        return { success: true, data: this.userInfo }
      }
      this.loading = true
      try {
        const res = await api.getUserInfo()
        if (res.code !== 200) {
          this.logout()
          return { success: false, error: `获取用户信息失败，错误码: ${res.code}` }
        }
        this.userInfo = res.data
        return { success: true, data: res.data }
      } catch (error) {
        this.logout()
        return { success: false, error: error.message || error }
      } finally {
        this.loading = false
      }
    },

    // 更新用户信息
    async updateUserInfo(userInfo = {}) {
      this.loading = true
      try {
        const res = await api.updateUser(userInfo)
        if (res.code === 200) {
          this.setUserInfo(userInfo)
          return { success: true }
        }
        return { success: false, error: res.msg }
      } catch (error) {
        console.error('更新用户信息失败:', error)
        return { success: false, error: error.message || error }
      } finally {
        this.loading = false
      }
    },

    // 设置用户信息（合并）
    setUserInfo(userInfo = {}) {
      this.userInfo = { ...this.userInfo, ...userInfo }
    },

    // 登出
    async logout() {
      removeToken()
      this.$reset()
      router.push('/')
      // 清空账本缓存
      const ledgerStore = useLedgerStore()
      ledgerStore.reset()
      // 清空交易缓存
      const transactionStore = useTransactionStore()
      transactionStore.reset()
    }
  },
  persist: {
    key: `${getConfig('appCode')}-user`,
    storage: localStorage,
    pick: ['userInfo']
  }
})
