import api from '@/api'

export const useLedgerStore = defineStore('ledger', {
  state() {
    return {
      // 账本列表
      ledgers: [],
      // 当前选中的账本
      currentLedger: null,
      // 账本模板列表
      templates: [],
      // 类别列表
      categories: [],
      // 加载状态
      loading: false,
      // 创建/更新加载状态
      loadingSubmit: false
    }
  },
  getters: {
    // 当前账本ID
    currentLedgerId() {
      return this.currentLedger?.id
    }
  },
  actions: {
    // 获取账本列表
    async fetchLedgerList() {
      this.loading = true
      try {
        const res = await api.getLedgerList()
        if (res.code === 200) {
          this.ledgers = res.data || []
          // 校验 currentLedger 是否仍在列表中
          if (this.currentLedger) {
            const exists = this.ledgers.find(l => l.id === this.currentLedger.id)
            if (!exists) {
              this.currentLedger = null
            }
          }
          // 如果没有当前选中账本且有账本列表，选中默认或第一个
          if (!this.currentLedger && this.ledgers.length > 0) {
            this.currentLedger = this.ledgers.find(l => l.is_default) || this.ledgers[0]
          }
        }
        return res
      } finally {
        this.loading = false
      }
    },

    // 获取账本模板列表
    async fetchTemplates() {
      try {
        const res = await api.getLedgerTemplates()
        if (res.code === 200) {
          this.templates = res.data || []
        }
        return res
      } catch (error) {
        console.error('获取账本模板失败:', error)
        return { code: -1, msg: error.message }
      }
    },

    // 从模板创建账本
    async createFromTemplate(templateId, name, description) {
      this.loadingSubmit = true
      try {
        const res = await api.createLedgerFromTemplate(templateId, { name, description })
        if (res.code === 200) {
          // 刷新账本列表
          await this.fetchLedgerList()
          // 刷新类别列表
          await this.fetchCategories()
        }
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 创建账本
    async createLedger(data) {
      this.loadingSubmit = true
      try {
        const res = await api.createLedger(data)
        if (res.code === 200) {
          await this.fetchLedgerList()
        }
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 更新账本
    async updateLedger(ledgerId, data) {
      this.loadingSubmit = true
      try {
        const res = await api.updateLedger(ledgerId, data)
        if (res.code === 200) {
          await this.fetchLedgerList()
        }
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 删除账本
    async deleteLedger(ledgerId) {
      this.loadingSubmit = true
      try {
        const res = await api.deleteLedger(ledgerId)
        if (res.code === 200) {
          // 如果删除的是当前账本，清除选中
          if (this.currentLedger?.id === ledgerId) {
            this.currentLedger = null
          }
          await this.fetchLedgerList()
        }
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 设为默认账本
    async setDefaultLedger(ledgerId) {
      this.loadingSubmit = true
      try {
        const res = await api.setDefaultLedger(ledgerId)
        if (res.code === 200) {
          await this.fetchLedgerList()
        }
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 获取类别列表
    async fetchCategories(txType = null) {
      try {
        const params = txType ? { type: txType } : {}
        const res = await api.getCategoryList(params)
        if (res.code === 200) {
          this.categories = res.data || []
        }
        return res
      } catch (error) {
        console.error('获取类别列表失败:', error)
        return { code: -1, msg: error.message }
      }
    },

    // 创建类别
    async createCategory(data) {
      this.loadingSubmit = true
      try {
        const res = await api.createCategory(data)
        if (res.code === 200) {
          await this.fetchCategories()
        }
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 更新类别
    async updateCategory(categoryId, data) {
      this.loadingSubmit = true
      try {
        const res = await api.updateCategory(categoryId, data)
        if (res.code === 200) {
          await this.fetchCategories()
        }
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 删除类别
    async deleteCategory(categoryId) {
      this.loadingSubmit = true
      try {
        const res = await api.deleteCategory(categoryId)
        if (res.code === 200) {
          await this.fetchCategories()
        }
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 获取系统预设类别
    async fetchSystemCategories(txType = null) {
      try {
        const params = txType ? { type: txType } : {}
        const res = await api.getSystemCategories(params)
        return res
      } catch (error) {
        console.error('获取系统预设类别失败:', error)
        return { code: -1, msg: error.message }
      }
    },

    // 切换当前账本
    setCurrentLedger(ledger) {
      this.currentLedger = ledger
    },

    // 重置状态
    reset() {
      this.ledgers = []
      this.currentLedger = null
      this.templates = []
      this.categories = []
      this.loading = false
      this.loadingSubmit = false
    }
  },
  persist: {
    key: 'ledger-store',
    storage: localStorage,
    pick: ['currentLedger']
  }
})
