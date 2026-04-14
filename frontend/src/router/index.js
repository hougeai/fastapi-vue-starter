import { createRouter, createWebHistory } from 'vue-router'
import { defaultRoutes } from './defaultRouter'
import { menuRouterFormatList } from './menuRouter' // 导入菜单路由
import { getToken, isNullOrWhitespace } from '@/utils'

const WHITE_LIST = ['/', '/404', '/reset-password']

export function createAuthGuard(router) {
  router.beforeEach(async to => {
    const token = getToken()

    /** 没有token的情况 */
    if (isNullOrWhitespace(token)) {
      if (WHITE_LIST.includes(to.path)) return true // 如果访问的是白名单页面（登录页或404），允许访问
      return { path: '/', query: { ...to.query, redirect: to.path } } // 否则重定向到登录页，并记录原目标路径
    }
    return true // 其他情况允许访问
  })
}

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'DefaultLayout',
      component: () => import('@/layout/DefaultLayout.vue'),
      redirect: '/',
      children: defaultRoutes
    },
    {
      path: '/home',
      name: 'DashboardLayout',
      component: () => import('@/layout/SidebarLayout.vue'),
      redirect: '/home',
      children: menuRouterFormatList // 格式化后的菜单路由
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    }
  ],
  scrollBehavior: () => ({ left: 0, top: 0 }) // 页面切换时滚动到顶部
})
