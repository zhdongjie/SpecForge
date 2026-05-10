import type { RouteRecordRaw } from 'vue-router'
import type { Menu, TemplateMenu } from '@/types/original/menu'
import { addDynamicRoutes } from '@/routes/dynamicRoutes'
import { findTreeNode } from '@/utils/tree'

const isTemplateMenu = (menu: Menu | null): menu is TemplateMenu => {
  return menu !== null && menu.type === 'TEMPLATE'
}

export default <RouteRecordRaw[]>[
  {
    path: '/',
    redirect: () => {
      const appStore = useAppStore()
      return { name: 'locale', params: { locale: appStore.language } }
    }
  },
  {
    path: '/:locale',
    name: 'locale',
    redirect: () => {
      const authorizeStore = useAuthorizeStore()
      const userStore = useUserStore()

      const isLoggedIn = authorizeStore.isLoggedIn
      const hasUserInfo = userStore.hasUserInfo

      if (isLoggedIn && hasUserInfo) {
        addDynamicRoutes()

        const menus = userStore.getMenus

        const firstMenus = findTreeNode('type', 'TEMPLATE', menus)

        if (isTemplateMenu(firstMenus)) {
          return typeof firstMenus.to === 'string'
            ? { name: firstMenus.to }
            : firstMenus.to
        }
      }

      return { name: 'authorize-login' }
    },
    children: [
      {
        path: 'authorize',
        name: 'authorize',
        redirect: { name: 'authorize-login' }
      },
      {
        path: 'authorize/login',
        name: 'authorize-login',
        meta: {
          public: true,
          title: 'Login',
          layout: 'blank',
          redirectIfLoggedIn: true
        },
        component: () => import('@/pages/authorize/login/index.vue')
      },
      {
        path: 'authorize/register',
        name: 'authorize-register',
        meta: {
          public: true,
          title: 'Register',
          layout: 'blank',
          redirectIfLoggedIn: true
        },
        component: () => import('@/pages/authorize/register/index.vue')
      },
      {
        path: 'error-404',
        name: 'error-404',
        meta: {
          public: true,
          title: '404',
          layout: 'blank'
        },
        component: () => import('@/pages/error/404/index.vue')
      }
    ]
  }
]
