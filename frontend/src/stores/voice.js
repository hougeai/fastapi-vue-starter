import api from '@/api'
import { getConfig } from '@/config/index'

export const useVoiceStore = defineStore('voice', {
  state: () => ({
    voices: [],
    lastFetchTime: null,
    loading: false,
    loadingNext: false,
    loadingDelete: false,
    loadingEdit: false,
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
    // 获取音色列表（智能缓存）
    async fetchVoices(forceRefresh = false) {
      // 如果有缓存且未过期，且不是强制刷新，直接返回
      if (!forceRefresh && this.voices.length > 0 && !this.isCacheExpired) {
        return this.voices
      }

      try {
        this.loading = true
        const response = await api.getVoiceList({ page: 1, page_size: 999 })
        this.voices = response?.data || []
        this.lastFetchTime = Date.now()
        return this.voices
      } catch (error) {
        console.error('获取音色列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 强制刷新音色列表
    async refreshVoices() {
      return this.fetchVoices(true)
    },

    // 上传音频
    async uploadAudio(formData) {
      try {
        this.loadingNext = true
        const response = await api.uploadAudio(formData)
        return response.data
      } catch (error) {
        console.error('上传音频失败:', error)
        throw error
      } finally {
        this.loadingNext = false
      }
    },
    // 克隆音频
    async cloneAudio(formData) {
      try {
        this.loadingNext = true
        const response = await api.cloneAudio(formData)
        return response.data
      } catch (error) {
        console.error('克隆音频失败:', error)
        throw error
      } finally {
        this.loadingNext = false
      }
    },

    // 创建音色
    async createVoice(data) {
      try {
        this.loadingNext = true
        const response = await api.createVoice(data)
        const newVoice = response.data
        // 将新音色添加到 voices 列表中（避免重复）
        if (!this.voices.some(v => v.id === newVoice.id)) {
          this.voices.unshift(newVoice) // 放在最前面，便于展示
        }
      } catch (error) {
        console.error('创建音色失败:', error)
        throw error
      } finally {
        this.loadingNext = false
      }
    },

    // 更新音色
    async updateVoice(data) {
      try {
        this.loadingEdit = true
        const response = await api.updateVoice(data)
        const updatedVoice = response.data
        // 更新 voices 列表中的音色
        const index = this.voices.findIndex(v => v.id === updatedVoice.id)
        if (index !== -1) {
          this.voices[index] = updatedVoice
        }
      } catch (error) {
        console.error('更新音色失败:', error)
        throw error
      } finally {
        this.loadingEdit = false
      }
    },

    // 删除音色
    async deleteVoice(id) {
      try {
        this.loadingDelete = true
        await api.deleteVoice({ id })
        this.voices = this.voices.filter(v => v.id !== id)
      } catch (error) {
        console.error('删除音色失败:', error)
        throw error
      } finally {
        this.loadingDelete = false
      }
    },

    // 清空缓存
    reset() {
      this.voices = []
      this.lastFetchTime = null
      this.loading = false
    }
  },

  // 持久化配置
  persist: {
    key: `${getConfig('appCode')}-voices`,
    storage: localStorage,
    // 只持久化歌单数据和最后获取时间
    pick: ['voices', 'lastFetchTime']
  }
})
