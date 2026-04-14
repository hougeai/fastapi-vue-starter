/**
 * 初始化加载效果的svg格式logo
 * @param {string} id - 元素id
 */
function initSvgLogo(id) {
  const appEl = document.querySelector(id)
  if (appEl) {
    const img = document.createElement('img')
    img.src = '/logo.svg'
    img.alt = 'logo'
    img.classList.add('loading-svg')
    appEl.appendChild(img)
  }
}
// 从 localStorage 读取主题色，并设置 css 变量 --primary-color
function addThemeColorCssVars() {
  const key = '__THEME_COLOR__'
  const defaultColor = '#1E88F4'
  const themeColor = window.localStorage.getItem(key) || defaultColor
  const cssVars = `--primary-color: ${themeColor}`
  document.documentElement.style.cssText = cssVars
}

addThemeColorCssVars()

initSvgLogo('#loadingLogo')
