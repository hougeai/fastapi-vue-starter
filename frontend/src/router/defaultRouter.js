export const defaultRoutes = [
  {
    path: '',
    name: 'LandingPage',
    meta: {
      title: 'Landing'
    },
    component: () => import('@/views/LandingPage.vue')
  },
  {
    path: '404',
    name: 'NotFoundPage',
    meta: {
      title: '页面未找到'
    },
    component: () => import('@/views/NotFoundPage.vue')
  }
]
