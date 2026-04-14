// 所有的 HTTP 请求都通过一个统一的 request 实例处理
import request from './http'

export default {
  // 用户相关
  refresh: () => request.post('/base/refresh_token'),
  getUserInfo: () => request.get('/base/userinfo'),
  phoneLogin: data => request.post('/base/phone_login', data),
  phoneRegister: data => request.post('/base/phone_register', data),
  updateUserInfo: (data = {}) => request.post('/user/update', data),
  fetchRoles: () => request.get('/base/user_roles'),
  // 产品相关
  getProductList: (params = {}) => request.get('/product/list', { params }),
  createProduct: (data = {}) => request.post('/product/create', data),
  updateProduct: (data = {}) => request.post('/product/update', data),
  deleteProduct: (params = {}) => request.delete('/product/delete', { params }),
  getProjectScripts: (params = {}) => request.get('/product/scripts', { params }),
  saveProjectScripts: (data = {}) => request.post('/product/scripts/save', data),
  generateProjectScripts: (data = {}) =>
    request.post('/product/scripts/generate', data, { timeout: 30000 }),
  uploadFile: data => request.post('/product/file/upload', data),
  // 音色相关
  getVoiceList: (params = {}) => request.get('/voice/list', { params }),
  uploadAudio: formData => request.post('/voice/upload', formData, { timeout: 30000 }),
  cloneAudio: formData => request.post('/voice/clone', formData, { timeout: 30000 }),
  createVoice: (data = {}) => request.post('/voice/create', data),
  updateVoice: (data = {}) => request.post('/voice/update', data),
  deleteVoice: (params = {}) => request.delete('/voice/delete', { params }),
  // 主播相关
  getHostList: (params = {}) => request.get('/agent/list-host', { params }),
  createHost: (data = {}) => request.post('/agent/create-host', data),
  updateHost: (data = {}) => request.post('/agent/update-host', data),
  deleteHost: (params = {}) => request.delete('/agent/delete-host', { params }),
  generateContent: (data = {}) => request.post('/agent/generate-content', data, { timeout: 60000 }),
  // 直播间相关
  getRoomList: (params = {}) => request.get('/room/list', { params }),
  createRoom: (data = {}) => request.post('/room/create', data),
  updateRoom: (data = {}) => request.post('/room/update', data),
  deleteRoom: (params = {}) => request.delete('/room/delete', { params })
}
