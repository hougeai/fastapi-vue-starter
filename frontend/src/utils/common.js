import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)
/**
 * @desc  格式化时间
 * @param {(Object|string|number)} time
 * @param {string} format
 * @returns {string | null}
 */
const formatDateTime = (time = undefined, format = 'YYYY-MM-DD HH:mm:ss', utc = false) => {
  if (utc) {
    return dayjs.utc(time).format(format)
  }
  return dayjs(time).format(format)
}

const formatDate = (date = undefined, format = 'YYYY-MM-DD') => {
  return formatDateTime(date, format)
}

// 格式化音频时长
const formatDuration = duration => {
  if (!duration) return '-'
  const hours = Math.floor(duration / 3600)
  const minutes = Math.floor((duration % 3600) / 60)
  const seconds = duration % 60

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  } else {
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }
}
// 文件大小格式化
const formatFileSize = bytes => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 遮挡密钥显示的函数
const maskKey = key => {
  if (!key) return ''
  if (key.length <= 4) return '*'.repeat(key.length)
  if (key.length <= 8)
    return key.substring(0, 2) + '*'.repeat(key.length - 4) + key.substring(key.length - 2)
  return key.substring(0, 4) + '*'.repeat(key.length - 8) + key.substring(key.length - 4)
}

// 金额格式化函数
const formatMoney = value => {
  return Number(value || 0).toFixed(2)
}

// 百分比格式化函数
const formatPercentage = (value, decimals = 2) => {
  if (value === null || value === undefined) return '0.00%'
  return (Number(value) * 100).toFixed(decimals) + '%'
}

export {
  formatDateTime,
  formatDate,
  formatDuration,
  formatFileSize,
  maskKey,
  formatMoney,
  formatPercentage
}
