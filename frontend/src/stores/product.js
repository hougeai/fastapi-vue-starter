import api from '@/api'
import { getConfig } from '@/config/index'

export const useProductStore = defineStore('product', {
  state: () => ({
    products: [],
    lastFetchTime: null,
    loading: false,
    loadingDelete: false,
    loadingScripts: false,
    loadingUpload: false,
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
    // 获取产品列表（智能缓存）
    async fetchProducts(forceRefresh = false) {
      // 如果有缓存且未过期，且不是强制刷新，直接返回
      if (!forceRefresh && this.products.length > 0 && !this.isCacheExpired) {
        return this.products
      }

      try {
        this.loading = true
        const response = await api.getProductList({ page: 1, page_size: 999 })
        this.products = response.data || []
        this.lastFetchTime = Date.now()
        return this.products
      } catch (error) {
        console.error('获取产品列表失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // 强制刷新产品列表
    async refreshProducts() {
      return this.fetchProducts(true)
    },

    async createProduct(data) {
      try {
        this.loading = true
        const response = await api.createProduct(data)
        const newProduct = response.data
        if (!this.products.some(v => v.id === newProduct.id)) {
          this.products.unshift(newProduct)
        }
        return newProduct
      } catch (error) {
        console.error('创建失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateProduct(data) {
      try {
        this.loading = true
        const response = await api.updateProduct(data)
        const updatedProduct = response.data
        // 更新 Products 列表
        const index = this.products.findIndex(v => v.id === updatedProduct.id)
        if (index !== -1) {
          this.products[index] = updatedProduct
        }
      } catch (error) {
        console.error('更新失败:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteProduct(id) {
      try {
        this.loadingDelete = true
        await api.deleteProduct({ id })
        this.products = this.products.filter(v => v.id !== id)
      } catch (error) {
        console.error('删除失败:', error)
        throw error
      } finally {
        this.loadingDelete = false
      }
    },

    // 脚本相关
    async getProjectScripts(project_id) {
      try {
        this.loadingScripts = true
        const response = await api.getProjectScripts({ project_id })
        return response.data
      } catch (error) {
        console.error('获取项目脚本失败:', error)
        throw error
      } finally {
        this.loadingScripts = false
      }
    },

    async saveProjectScripts(data) {
      try {
        this.loadingScripts = true
        const response = await api.saveProjectScripts(data)
        return response.data
      } catch (error) {
        console.error('保存项目脚本失败:', error)
        throw error
      } finally {
        this.loadingScripts = false
      }
    },

    async generateProjectScripts(data) {
      try {
        this.loadingScripts = true
        const response = await api.generateProjectScripts(data)
        return response.data
      } catch (error) {
        console.error('生成项目脚本失败:', error)
        throw error
      } finally {
        this.loadingScripts = false
      }
    },

    async uploadFile(data) {
      try {
        this.loadingUpload = true
        const response = await api.uploadFile(data)
        return response.data
      } catch (error) {
        console.error('上传文件失败:', error)
        throw error
      } finally {
        this.loadingUpload = false
      }
    },

    // 清空产品缓存
    reset() {
      this.products = []
      this.lastFetchTime = null
      this.loading = false
    }
  },

  // 持久化配置
  persist: {
    key: `${getConfig('appCode')}-product`,
    storage: localStorage,
    // 只持久化设备数据和最后获取时间
    pick: ['products', 'lastFetchTime']
  }
})
