import api from '@/api'
import { getConfig } from '@/config/index'
import { useHostStore } from './host'

const hostStore = useHostStore()

export const useRoomStore = defineStore('room', {
  state: () => ({
    rooms: [],
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
    async fetchRooms(forceRefresh = false) {
      if (!forceRefresh && this.rooms.length > 0 && !this.isCacheExpired) {
        return this.rooms
      }
      try {
        this.loading = true
        const response = await api.getRoomList({ page: 1, page_size: 999 })
        this.rooms = response?.data || []
        // 获取host详细信息
        const hosts = await hostStore.fetchHosts()
        await Promise.all(
          this.rooms.map(async room => {
            if (room.host_agent_id) {
              room.host_agent = hosts.find(host => host.id === room.host_agent_id)
            }
          })
        )
        this.lastFetchTime = Date.now()
        return this.rooms
      } catch (error) {
        console.error('获取直播间列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 强制刷新直播间列表
    async refreshRooms() {
      return this.fetchRooms(true)
    },

    async getRoom(id) {
      const room = this.rooms.find(v => v.id == id)
      return room
    },

    async createRoom(data) {
      try {
        this.loading = true
        const response = await api.createRoom(data)
        const newRoom = response.data
        // 获取host详细信息
        const hosts = await hostStore.fetchHosts()
        newRoom.host_agent = hosts.find(host => host.id === newRoom.host_agent_id)
        if (!this.rooms.some(v => v.id === newRoom.id)) {
          this.rooms.unshift(newRoom) // 放在最前面，便于展示
        }
        return newRoom
      } catch (error) {
        console.error('创建直播间失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateRoom(data) {
      try {
        this.loading = true
        const response = await api.updateRoom(data)
        const updatedRoom = response.data
        // 获取host详细信息
        const hosts = await hostStore.fetchHosts()
        updatedRoom.host_agent = hosts.find(host => host.id === updatedRoom.host_agent_id)
        // 更新 rooms 列表
        const index = this.rooms.findIndex(v => v.id === updatedRoom.id)
        if (index !== -1) {
          this.rooms[index] = updatedRoom
        }
        AMessage.success('更新直播间成功')
      } catch (error) {
        console.error('更新直播间失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteRoom(id) {
      try {
        this.loadingDelete = true
        await api.deleteRoom({ id })
        this.rooms = this.rooms.filter(v => v.id !== id)
      } catch (error) {
        console.error('删除直播间失败:', error)
        throw error
      } finally {
        this.loadingDelete = false
      }
    }
  },

  // 持久化配置
  persist: {
    key: `${getConfig('appCode')}-rooms`,
    storage: localStorage,
    // 只持久化歌单数据和最后获取时间
    pick: ['rooms', 'lastFetchTime']
  }
})
