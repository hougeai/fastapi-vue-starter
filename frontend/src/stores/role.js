import api from '@/api'
import { getConfig } from '@/config/index'
import { formatFileSize } from '@/utils/common'
const navEntry = window.performance?.getEntriesByType?.('navigation')?.[0]
let reloadFlag = navEntry?.type === 'reload'

export const useRoleStore = defineStore('role', {
  state: () => ({
    roles: [], // 原始后端 Role 数据
    lastFetchTime: null, // 上次拉取时间戳
    loading: false,
    // 缓存有效期：60分钟
    cacheExpiry: 60 * 60 * 1000
  }),

  getters: {
    // 检查缓存是否过期
    isCacheExpired: state => {
      if (!state.lastFetchTime) return true
      return Date.now() - state.lastFetchTime > state.cacheExpiry
    },

    // 通过 id 获取角色
    getRoleById: state => id => {
      return state.roles.find(r => r.id === id)
    },

    // 根据后端 Role 字段映射为前端展示用的 Plan，自动构建 perks
    plans: state => {
      const mapped = (state.roles || []).map(r => ({
        id: r.id,
        name: r.name,
        desc: r.desc || '',
        monthly: Number(r.price_monthly ?? 0),
        yearly: Number(r.price_yearly ?? 0),
        perks: buildPerks(r)
      }))

      // 追加企业定制（前端写死）
      const enterprisePlan = {
        id: 999,
        name: '企业定制',
        desc: '企业定制与专属支持',
        monthly: 0,
        yearly: 0,
        perks: ['私有化部署', '自定义功能', 'SLA 保障', '专属技术支持']
      }

      return [...mapped, enterprisePlan]
    }
  },

  actions: {
    // 获取角色列表（智能缓存）
    async fetchRoles(forceRefresh = false) {
      // 当强制刷新或者用户按F5，强制刷新角色数据
      let shouldForceRefresh = forceRefresh
      if (!shouldForceRefresh) {
        if (reloadFlag) {
          shouldForceRefresh = true
          reloadFlag = false // 消费掉，仅在本次F5后的“第一次”进入页面生效
        }
      }
      if (!shouldForceRefresh && this.roles.length > 0 && !this.isCacheExpired) {
        return this.roles
      }

      try {
        this.loading = true
        const response = await api.fetchRoles()
        this.roles = response?.data || []
        this.lastFetchTime = Date.now()
        return this.roles
      } catch (error) {
        console.error('获取角色列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 强制刷新
    async refreshRoles() {
      return this.fetchRoles(true)
    },

    // 清空角色缓存
    reset() {
      this.roles = []
      this.lastFetchTime = null
      this.loading = false
    }
  },

  // 持久化配置
  persist: {
    key: `${getConfig('appCode')}-role`,
    storage: localStorage,
    // 只持久化角色数据和最后获取时间
    pick: ['roles', 'lastFetchTime']
  }
})

// 工具：根据后端字段构建权益文案
function buildPerks(r) {
  const perks = []
  perks.push(`设备绑定上限：${formatLimit(r.max_devices, '台')}`)
  perks.push(`闹钟设置总量：${formatLimit(r.max_alarms, '个')}`)
  perks.push(`每日音乐播放：${formatDaily(r.max_dailyplay)}`)
  perks.push(`设备歌单容量：${formatLimit(r.max_playlist, '首')}`)
  perks.push(`上传歌曲数量：${formatLimit(r.max_upload_songs, '首')}`)
  perks.push(`自研知识库存储：${formatFileSize(r.kb_file_quota)}`)
  perks.push(`Dify知识库接入：${formatLimit(r.kb_dify_limit)}`)
  perks.push('更新设备屏幕显示')
  perks.push('查看/下载聊天记录')
  if (r.id > 3) {
    perks.push('新功能抢先体验')
  }
  return perks
}

// 数值上限格式化
function isUnlimited(n) {
  // 约定：负数/极大数均视为不限
  return n < 0 || n >= 9999
}
function formatLimit(n, unit = '') {
  if (isUnlimited(Number(n))) return '不限'
  return `${n} ${unit}`.trim()
}
function formatDaily(n) {
  if (isUnlimited(Number(n))) return '不限'
  return `${n} 次`
}
