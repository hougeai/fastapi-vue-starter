// 所有的 HTTP 请求都通过一个统一的 request 实例处理
import request from './http'

export default {
  // ============ 认证相关 ============
  // 刷新 Token
  refreshToken: () => request.post('/base/refresh_token'),
  // 获取用户信息
  getUserInfo: () => request.get('/base/userinfo'),
  // 获取用户菜单
  getUserMenu: () => request.get('/base/usermenu'),
  // 邮箱登录
  emailLogin: data => request.post('/base/email_login', data),
  // 发送验证码
  sendVerifyCode: data => request.post('/base/verifycode', data),
  // 用户注册
  register: data => request.post('/base/register', data),

  // ============ 用户管理 ============
  // 用户列表
  getUserList: params => request.get('/user/list', { params }),
  // 用户详情
  getUser: params => request.get('/user/get', { params }),
  // 更新用户
  updateUser: data => request.post('/user/update', data),
  // 删除用户
  deleteUser: params => request.delete('/user/delete', { params }),

  // ============ 账本模板 ============
  // 获取账本模板列表
  getLedgerTemplates: () => request.get('/ledger/template'),
  // 创建账本模板（管理员）
  createLedgerTemplate: data => request.post('/ledger/template', data),
  // 从模板创建账本
  createLedgerFromTemplate: (templateId, params) =>
    request.post(`/ledger/template/${templateId}/create`, null, { params }),

  // ============ 账本 ============
  // 创建账本
  createLedger: data => request.post('/ledger', data),
  // 获取账本列表
  getLedgerList: () => request.get('/ledger'),
  // 获取账本详情
  getLedger: params => request.get('/ledger', { params }),
  // 更新账本
  updateLedger: (ledgerId, data) => request.put(`/ledger/${ledgerId}`, data),
  // 删除账本
  deleteLedger: ledgerId => request.delete(`/ledger/${ledgerId}`),
  // 设为默认账本
  setDefaultLedger: ledgerId => request.post(`/ledger/${ledgerId}/default`),

  // ============ 类别 ============
  // 创建类别
  createCategory: data => request.post('/ledger/category', data),
  // 获取类别列表
  getCategoryList: params => request.get('/ledger/category', { params }),
  // 更新类别
  updateCategory: (categoryId, data) => request.put(`/ledger/category/${categoryId}`, data),
  // 删除类别
  deleteCategory: categoryId => request.delete(`/ledger/category/${categoryId}`),
  // 获取系统预设类别
  getSystemCategories: params => request.get('/ledger/category/system', { params }),

  // ============ 交易记录 ============
  // 创建交易记录
  createTransaction: data => request.post('/transaction', data),
  // 获取交易记录列表
  getTransactionList: params => request.get('/transaction', { params }),
  // 获取收支汇总
  getTransactionSummary: params => request.get('/transaction/summary', { params }),
  // 获取交易记录详情
  getTransaction: transactionId => request.get(`/transaction/${transactionId}`),
  // 更新交易记录
  updateTransaction: (transactionId, data) => request.put(`/transaction/${transactionId}`, data),
  // 删除交易记录
  deleteTransaction: transactionId => request.delete(`/transaction/${transactionId}`),
}
