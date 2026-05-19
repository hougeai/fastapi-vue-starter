import IconHome from '~icons/material-symbols/home'
import IconWallet from '~icons/material-symbols/account-balance-wallet-outline'
import IconReceipt from '~icons/material-symbols/receipt-long-outline'
import IconBarChart from '~icons/material-symbols/bar-chart-4-bars'
import IconUser from '~icons/material-symbols/person'

export const menuRouter = [
  {
    path: 'home',
    name: 'Home',
    meta: {
      title: '首页',
      icon: markRaw(IconHome)
    },
    component: () => import('@/views/HomePage.vue')
  },
  {
    path: 'ledgers',
    name: 'LedgerPage',
    meta: {
      title: '账本管理',
      icon: markRaw(IconWallet)
    },
    component: () => import('@/views/LedgerPage.vue')
  },
  {
    path: 'transactions',
    name: 'TransactionPage',
    meta: {
      title: '交易记录',
      icon: markRaw(IconReceipt)
    },
    component: () => import('@/views/TransactionPage.vue')
  },
  {
    path: 'reports',
    name: 'ReportPage',
    meta: {
      title: '报表',
      icon: markRaw(IconBarChart)
    },
    component: () => import('@/views/ReportPage.vue')
  },
  {
    path: 'profile',
    name: 'ProfilePage',
    meta: {
      title: '我的',
      icon: markRaw(IconUser)
    },
    component: () => import('@/views/ProfilePage.vue')
  }
]

export const menuRouterFormat = (router, parentPath) => {
  return router.map(item => {
    // 拼接路由，例：'devtools' -> '/devtools'  'regular' -> '/devtools/regular'
    item.path = parentPath ? `${parentPath}/${item.path}` : `/${item.path}`

    // 存在 children 属性，且 children 数组长度大于 0，开始递归
    if (item.children && item.children.length > 0) {
      item.children = menuRouterFormat(item.children, item.path)
    }

    return Object.assign({}, item, item.meta || {})
  })
}

// 解析后 路由菜单列表
export const menuRouterFormatList = menuRouterFormat([...menuRouter])
