// 获取环境变量
const ENV = import.meta.env
// 引入本地默认头像
import defaultAvatar from '@/assets/img/avatar.webp'

// 配置文件
let config = {}
// 默认配置文件
const configSource = {
  appCode: ENV.VITE_APP_CODE,
  // 项目名
  projectName: ENV.VITE_APP_NAME,
  // 项目描述
  projectTitle: ENV.VITE_APP_TITLE,
  projectDesc: ENV.VITE_APP_DESCRIPTION,
  // 后端接口路径
  baseURL: ENV.VITE_BASE_URL,
  // 对象存储路径
  ossUrl: ENV.VITE_OSS_BUCKET_URL,
  wsUrl: ENV.VITE_WS_URL,
  // 个人配置
  me: {
    gzhName: ENV.VITE_GZH_NAME,
    gzhUrl: ENV.VITE_GZH_URL,
    name: ENV.VITE_ME_NAME,
    github: ENV.VITE_GITHUB_URL,
    icp: ENV.VITE_ICP,
    avatar: defaultAvatar || ENV.VITE_AVATAR,
    feishuDoc: ENV.VITE_FEISHU_DOC_URL
  },
  // 语言选项配置
  languageOptions: [
    { label: '全部语言', value: '全部语言' },
    { label: '中文', value: 'chinese' },
    { label: '英语', value: 'english' },
    { label: '日语', value: 'japanese' },
    { label: '韩语', value: 'korean' },
    { label: '德语', value: 'german' },
    { label: '法语', value: 'french' },
    { label: '西班牙语', value: 'spanish' },
    { label: '阿拉伯语', value: 'arabic' }
  ],
  // 发货类型配置
  deliveryOptions: [
    { label: '实物发货', value: 'physical' },
    { label: '虚拟发货', value: 'virtual' },
    { label: '无需发货', value: 'none' }
  ],
  // 直播平台
  platformOptions: [
    { label: '抖音', value: 'douyin' },
    { label: 'TikTok', value: 'tiktok' }
  ]
}

const setConfig = cfg => {
  config = Object.assign(config, cfg)
  return config
}

const resetConfig = () => {
  config = { ...configSource }
  return config
}

resetConfig() // 初始化需要调用一次

const getConfig = key => {
  if (typeof key === 'string') {
    const arr = key.split('.')
    if (arr && arr.length) {
      let data = config
      arr.forEach(v => {
        if (data && typeof data[v] !== 'undefined') {
          data = data[v]
        } else {
          data = null
        }
      })
      return data
    }
  }
  if (Array.isArray(key)) {
    const data = config
    if (key && key.length > 1) {
      let res = {}
      key.forEach(v => {
        if (data && typeof data[v] !== 'undefined') {
          res[v] = data[v]
        } else {
          res[v] = null
        }
      })
      return res
    }
    return data[key]
  }
  return { ...config }
}

// 获取语言标签
const getLanguageLabel = value => {
  const languageOptions = configSource.languageOptions
  const option = languageOptions.find(option => option.value === value)
  return option ? option.label : value || '-'
}

// 获取交付类型标签
const getDeliveryLabel = value => {
  const deliveryOptions = configSource.deliveryOptions
  const option = deliveryOptions.find(option => option.value === value)
  return option ? option.label : value || '-'
}

// 获取直播平台标签
const getPlatformLabel = value => {
  const platformOptions = configSource.platformOptions
  const option = platformOptions.find(option => option.value === value)
  return option ? option.label : value || '-'
}

export { getConfig, setConfig, resetConfig, getLanguageLabel, getDeliveryLabel, getPlatformLabel }
