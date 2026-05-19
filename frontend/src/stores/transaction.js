import api from '@/api'
import dayjs from 'dayjs'

export const useTransactionStore = defineStore('transaction', {
  state() {
    return {
      // 交易记录列表
      transactions: [],
      // 总数
      total: 0,
      // 当前页
      page: 1,
      // 每页条数
      pageSize: 20,
      // 收支汇总
      summary: {
        total_income: 0,
        total_expense: 0,
        balance: 0,
        count: 0
      },
      // 加载状态
      loading: false,
      // 提交加载状态
      loadingSubmit: false
    }
  },
  actions: {
    // 获取交易记录列表
    async fetchTransactions(params = {}) {
      this.loading = true
      try {
        const res = await api.getTransactionList({
          ledger_id: params.ledgerId,
          page: params.page || this.page,
          page_size: params.pageSize || this.pageSize,
          type: params.txType,
          category_id: params.categoryId,
          start_date: params.startDate,
          end_date: params.endDate
        })
        if (res.code === 200) {
          this.transactions = res.data?.data || []
          this.total = res.data?.total || 0
          this.page = res.data?.page || 1
          this.pageSize = res.data?.page_size || 20
        }
        return res
      } finally {
        this.loading = false
      }
    },

    // 获取收支汇总
    async fetchSummary(ledgerId, txType = null, startDate = null, endDate = null) {
      try {
        const res = await api.getTransactionSummary({
          ledger_id: ledgerId,
          type: txType,
          start_date: startDate,
          end_date: endDate
        })
        if (res.code === 200) {
          this.summary = res.data || {
            total_income: 0,
            total_expense: 0,
            balance: 0,
            count: 0
          }
        }
        return res
      } catch (error) {
        console.error('获取收支汇总失败:', error)
        return { code: -1, msg: error.message }
      }
    },

    // 获取月度汇总（前端聚合）
    async fetchMonthlySummary(ledgerId, year, month) {
      const startDate = dayjs(`${year}-${month}-01`).startOf('month').format('YYYY-MM-DD')
      const endDate = dayjs(`${year}-${month}-01`).endOf('month').format('YYYY-MM-DD')
      return this.fetchSummary(ledgerId, null, startDate, endDate)
    },

    // 获取年度汇总（前端聚合）
    async fetchYearlySummary(ledgerId, year) {
      const startDate = `${year}-01-01`
      const endDate = `${year}-12-31`
      return this.fetchSummary(ledgerId, null, startDate, endDate)
    },

    // 创建交易记录
    async createTransaction(data) {
      this.loadingSubmit = true
      try {
        const res = await api.createTransaction(data)
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 更新交易记录
    async updateTransaction(transactionId, data) {
      this.loadingSubmit = true
      try {
        const res = await api.updateTransaction(transactionId, data)
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 删除交易记录
    async deleteTransaction(transactionId) {
      this.loadingSubmit = true
      try {
        const res = await api.deleteTransaction(transactionId)
        return res
      } finally {
        this.loadingSubmit = false
      }
    },

    // 重置状态
    reset() {
      this.transactions = []
      this.total = 0
      this.page = 1
      this.pageSize = 20
      this.summary = {
        total_income: 0,
        total_expense: 0,
        balance: 0,
        count: 0
      }
      this.loading = false
      this.loadingSubmit = false
    }
  },
  persist: {
    key: 'transaction-store',
    storage: localStorage,
    pick: ['page', 'pageSize']
  }
})
