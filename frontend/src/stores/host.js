import api from '@/api'
import { getConfig } from '@/config/index'

export const useHostStore = defineStore('host', {
  state: () => ({
    hosts: [],
    lastFetchTime: null,
    loading: false,
    loadingDelete: false,
    loadingGenerate: false,
    // 缓存有效期：30分钟
    cacheExpiry: 30 * 60 * 1000
  }),

  getters: {
    // 检查缓存是否过期
    isCacheExpired: state => {
      if (!state.lastFetchTime) return true
      return Date.now() - state.lastFetchTime > state.cacheExpiry
    }
  },

  actions: {
    async fetchHosts(forceRefresh = false) {
      if (!forceRefresh && this.hosts.length > 0 && !this.isCacheExpired) {
        return this.hosts
      }
      try {
        this.loading = true
        const response = await api.getHostList({ page: 1, page_size: 999 })
        this.hosts = response?.data || []
        this.lastFetchTime = Date.now()
        return this.hosts
      } catch (error) {
        console.error('获取主播列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 强制刷新主播列表
    async refreshHosts() {
      return this.fetchHosts(true)
    },

    async createHost(data) {
      try {
        this.loading = true
        const response = await api.createHost(data)
        const newHost = response.data
        if (!this.hosts.some(v => v.id === newHost.id)) {
          this.hosts.unshift(newHost) // 放在最前面，便于展示
        }
      } catch (error) {
        console.error('创建主播失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateHost(data) {
      try {
        this.loading = true
        const response = await api.updateHost(data)
        const updatedHost = response.data
        // 更新 hosts 列表
        const index = this.hosts.findIndex(v => v.id === updatedHost.id)
        if (index !== -1) {
          this.hosts[index] = updatedHost
        }
      } catch (error) {
        console.error('更新主播失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteHost(id) {
      try {
        this.loadingDelete = true
        await api.deleteHost({ id })
        this.hosts = this.hosts.filter(v => v.id !== id)
      } catch (error) {
        console.error('删除主播失败:', error)
        throw error
      } finally {
        this.loadingDelete = false
      }
    },

    // 生成主播背景等内容
    async generateContent(data) {
      try {
        this.loadingGenerate = true
        const response = await api.generateContent(data)
        return response.data || {}
      } catch (error) {
        console.error('生成主播背景等失败，请稍候重试或手动填写:', error)
        throw error
      } finally {
        this.loadingGenerate = false
      }
    }
  },

  // 持久化配置
  persist: {
    key: `${getConfig('appCode')}-hosts`,
    storage: localStorage,
    // 只持久化歌单数据和最后获取时间
    pick: ['hosts', 'lastFetchTime']
  }
})
