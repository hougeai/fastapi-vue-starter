import IconHome from '~icons/material-symbols/home'
import IconDashboard from '~icons/material-symbols/dashboard-outline'
import IconUser from '~icons/material-symbols/person'
import IconLive from '~icons/material-symbols/live-tv-outline'
import IconProject from '~icons/material-symbols/production-quantity-limits'
import IconHost from '~icons/material-symbols/psychology-outline'
import IconVoice from '~icons/material-symbols/auto-detect-voice'
import IconInfo from '~icons/material-symbols/person-edit-outline'
import IconOrder from '~icons/material-symbols/assignment-outline'
import IconInvite from '~icons/material-symbols/person-add-outline'
import IconMoney from '~icons/material-symbols/money-bag'

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
    path: 'dashboard',
    name: 'Dashboard',
    meta: {
      title: '控制台',
      icon: markRaw(IconDashboard)
    },
    redirect: { name: 'LiveRoomPage' },
    children: [
      {
        path: 'live-room',
        name: 'LiveRoomPage',
        meta: {
          title: '我的直播间',
          icon: markRaw(IconLive)
        },
        component: () => import('@/views/dashboard/LiveRoomPage.vue'),
        children: [
          {
            path: 'create',
            name: 'CreateLiveRoom',
            meta: {
              hideParentContent: true
            },
            component: () => import('@/views/dashboard/LiveRoomForm.vue')
          },
          {
            path: 'edit/:id',
            name: 'EditLiveRoom',
            meta: {
              hideParentContent: true
            },
            component: () => import('@/views/dashboard/LiveRoomForm.vue')
          }
        ]
      },
      {
        path: 'product',
        name: 'ProductPage',
        meta: {
          title: '我的项目',
          icon: markRaw(IconProject)
        },
        component: () => import('@/views/dashboard/ProductPage.vue')
      },
      {
        path: 'host-agent',
        name: 'HostAgentPage',
        meta: {
          title: '我的主播',
          icon: markRaw(IconHost)
        },
        component: () => import('@/views/dashboard/HostAgentPage.vue')
      },
      {
        path: 'voice',
        name: 'VoicePage',
        meta: {
          title: '音色管理',
          icon: markRaw(IconVoice)
        },
        component: () => import('@/views/dashboard/VoicePage.vue')
      }
    ]
  },
  {
    path: 'user-center',
    name: 'UserCenter',
    meta: {
      title: '个人中心',
      icon: markRaw(IconUser)
    },
    redirect: { name: 'UserInfoPage' },
    children: [
      {
        path: 'user-info',
        name: 'UserInfoPage',
        meta: {
          title: '个人资料',
          icon: markRaw(IconInfo)
        },
        component: () => import('@/views/user-center/UserInfoPage.vue')
      },
      {
        path: 'user-order',
        name: 'UserOrderPage',
        meta: {
          title: '我的订单',
          icon: markRaw(IconOrder)
        },
        component: () => import('@/views/user-center/UserOrderPage.vue')
      },
      {
        path: 'user-invite',
        name: 'UserInvitePage',
        meta: {
          title: '我的邀请',
          icon: markRaw(IconInvite)
        },
        component: () => import('@/views/user-center/UserInvitePage.vue')
      },
      {
        path: 'user-balance',
        name: 'UserBalancePage',
        meta: {
          title: '我的余额',
          icon: markRaw(IconMoney)
        },
        component: () => import('@/views/user-center/UserBalancePage.vue')
      }
    ]
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
