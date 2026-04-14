import api from '@/api'
import { removeToken, formatDate } from '@/utils'
import { getConfig } from '@/config/index'
import { router } from '@/router'
import { useProductStore } from './product'
import { useRoleStore } from './role'

export const useUserStore = defineStore('user', {
  state() {
    return {
      userInfo: {}
    }
  },
  // getters直接返回属性，直接用userStore.name而不需要userStore.userInfo.user_name
  getters: {
    userId() {
      return this.userInfo?.user_id
    },
    userName() {
      return this.userInfo?.user_name
    },
    email() {
      return this.userInfo?.email
    },
    phone() {
      return this.userInfo?.phone
    },
    wxid() {
      return this.userInfo?.wxid
    },
    roleId() {
      return this.userInfo?.role_id || 0
    },
    roleName() {
      return this.userInfo?.role_name || '未知角色'
    },
    roleDesc() {
      return this.userInfo?.role_desc || '暂无描述'
    },
    roleExpire() {
      return this.userInfo?.role_expire ? formatDate(this.userInfo.role_expire) : '永久'
    },
    avatar() {
      return this.userInfo?.avatar || getConfig('me.avatar')
    }
  },
  actions: {
    async getUserInfo(forceRefresh = false) {
      if (!forceRefresh && Object.keys(this.userInfo).length > 0) {
        return { success: true, data: this.userInfo }
      }
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
      }
    },
    async logout() {
      removeToken()
      this.$reset() // 清除persist的数据
      router.push('/')
      // 清空产品缓存
      const productStore = useProductStore()
      productStore.reset()
      // 清空角色缓存
      const roleStore = useRoleStore()
      roleStore.reset()
    },
    async updateUserInfo(userInfo = {}) {
      try {
        await api.updateUserInfo(userInfo)
        this.setUserInfo(userInfo)
        return { success: true }
      } catch (error) {
        console.error('更新用户信息失败:', error)
        return { success: false, error: error.message || error }
      }
    },
    setUserInfo(userInfo = {}) {
      // 保留原对象中未更新的字段，新对象中的值覆盖同名字段，避免手动指定要保留的字段
      this.userInfo = { ...this.userInfo, ...userInfo }
    }
  },
  persist: {
    key: `${getConfig('appCode')}-user`,
    storage: localStorage,
    pick: ['userInfo']
  }
})
