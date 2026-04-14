import axios from 'axios'
import { getToken, setToken } from '@/utils'
import { useUserStore } from '@/stores/user'
import { getConfig } from '@/config'

function resolveResError(code, message) {
  switch (code) {
    case 400:
      message = message ?? '请求参数错误'
      break
    case 401:
      message = message ?? '无效的Token'
      break
    case 419:
      message = message ?? '登录已过期'
      break
    case 403:
      message = message ?? '没有权限'
      break
    case 404:
      message = message ?? '资源或接口不存在'
      break
    case 500:
      message = message ?? '服务器异常'
      break
    default:
      message = message ?? `【${code}】: 未知异常!`
      break
  }
  return message
}

// 请求成功拦截器
function reqResolve(config) {
  // 处理不需要token的请求
  if (config.noNeedToken) {
    return config
  }
  // 这个token来自localStorage
  const token = getToken()
  if (token) {
    config.headers.token = config.headers.token || token
  }
  return config
}

//请求失败拦截器
function reqReject(error) {
  return Promise.reject(error) // 直接抛出错误，传给前端的catch处理
}

// 响应成功拦截器
function resResolve(response) {
  const { data, status, statusText } = response
  // 网络层面成功，但是业务层面失败
  if (data?.code !== 200) {
    // ?? 运算符：当 data.code为 null 或 undefined 时，则返回status
    const code = data?.code ?? status
    /** 根据code处理对应的操作，并返回处理后的message */
    const message = resolveResError(code, data?.msg ?? statusText)
    AMessage.error(message)
    return Promise.reject({ code, message, error: data || response }) // catch时也会接收三个值
  }
  return Promise.resolve(data)
}

function createInterceptors(service) {
  // 请求拦截器
  service.interceptors.request.use(reqResolve, reqReject)
  // 响应拦截器，分别处理成功响应-2xx，和失败响应-4xx/5xx
  service.interceptors.response.use(resResolve, async function (error) {
    // 处理网络错误等
    if (!error || !error.response) {
      const code = error?.code
      /** 根据code处理对应的操作，并返回处理后的message */
      const message = resolveResError(code, error.message)
      AMessage.error(message)
      return Promise.reject({ code, message, error })
    }
    const { data, status, config } = error.response
    // 处理419登录过期
    if (data?.code === 419) {
      try {
        const res = await service.post('/base/refresh_token')
        setToken(res.data.access_token)
        // 重试之前失败的请求
        config.headers.token = res.data.access_token
        console.log('refresh token success', res)
        return service(config)
      } catch (error) {
        console.log('refresh token error', error)
        // refresh token 也失败了,执行登出
        const userStore = useUserStore()
        userStore.logout()
        return Promise.reject(error)
      }
    }
    // 处理401未授权
    if (data?.code === 401) {
      try {
        const userStore = useUserStore()
        userStore.logout()
        return Promise.reject(error)
      } catch (error) {
        console.log('resReject error', error)
        return
      }
    }
    // 后端返回的response数据
    const code = data?.code ?? status
    const message = resolveResError(code, data?.msg ?? error.message)
    AMessage.error(message)
    return Promise.reject({ code, message, error: error.response?.data || error.response })
  })
}

function createAxios() {
  const service = axios.create({
    baseURL: getConfig('baseURL'),
    timeout: 12000,
    transformRequest: [
      function (data, headers) {
        if (data instanceof FormData) {
          // 对于 FormData，让浏览器自动处理 Content-Type
          delete headers['Content-Type']
          return data
        }
        if (typeof data === 'object') {
          headers['Content-Type'] = 'application/json'
          return JSON.stringify(data)
        }
        return data
      }
    ]
  })
  // 添加请求和响应拦截器
  createInterceptors(service)
  return service
}

const request = createAxios()

export default request
