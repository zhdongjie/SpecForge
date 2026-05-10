import type { RouteRecordRaw } from 'vue-router'
import type { Menu, SubMenu } from '@/types/original/menu'
import type { Router, User } from '@/types/original/store'
import { meApi } from '@/api'

const STORE_KEY = 'original-user'
const VIEW_MODULES = import.meta.glob('@/pages/**/*.vue')

/**
 * format router path to name
 */
const formatRoutePathToName = (routerPath: string) => {
  return formatRoutePath(routerPath).replace(/\//g, '-')
}

/**
 * format router path
 */
const formatRoutePath = (routerPath: string) => {
  return routerPath.replace(/^\//, '')
}

/**
 * check if a menu is a SubMenu type
 */
const isSubMenu = (menu: Menu): menu is SubMenu => {
  return (
    menu.type === 'GROUP' || menu.type === 'TEMPLATE' || menu.type === 'LINK'
  )
}

/**
 * create menu item from router config
 */
const createMenuFromRouter = (router: Router): Menu => {
  const baseMenu = {
    id: router.id,
    parentId: router.parentId,
    name: router.name,
    icon: router.icon,
    badgeContent: router.badgeContent,
    badgeColor: router.badgeColor,
    sort: router.sort,
    children: []
  }

  switch (router.type) {
    case 'TEMPLATE':
      return {
        ...baseMenu,
        type: router.type,
        to: formatRoutePathToName(router.routerPath)
      }
    case 'LINK':
      return {
        ...baseMenu,
        type: router.type,
        to: { href: router.href, target: router.target }
      }
    case 'SUBHEADER':
    case 'GROUP':
    default:
      return { ...baseMenu, type: router.type }
  }
}

export const useUserStore = defineStore(STORE_KEY, {
  state: (): User => ({
    username: '',
    gender: undefined,
    birthday: undefined,
    email: undefined,
    phoneNumber: undefined,
    avatar: undefined,
    roles: [],
    routers: [],
    buttons: [],
    createdTime: ''
  }),

  getters: {
    /**
     * check if user is logged in
     */
    hasUserInfo: (state) => !!state.username,

    /**
     * get router configuration
     */
    getRouters: (state): RouteRecordRaw[] => {
      return state.routers
        .filter((router) => router.type === 'TEMPLATE')
        .map((router) => {
          const routerPath = router.routerPath
          return {
            path: formatRoutePath(routerPath),
            name: formatRoutePathToName(routerPath),
            component: VIEW_MODULES[`/src/pages${router.componentPath}`],
            meta: {
              dynamic: true,
              title: router.name,
              layout: 'content'
            }
          }
        })
    },

    /**
     * build menu tree
     */
    getMenus: (state) => {
      const visibleRouters = state.routers.filter((router) => router.visible)
      const menuMap = new Map<string, Menu>()

      // create all menu items
      visibleRouters.forEach((router) => {
        menuMap.set(router.id, createMenuFromRouter(router))
      })

      // build menu tree
      const rootMenus: Menu[] = []

      menuMap.forEach((menu) => {
        if (String(menu.parentId) === '0') {
          rootMenus.push(menu)
        } else {
          const parentMenu = menuMap.get(menu.parentId)
          if (parentMenu) {
            // 检查menu是否可以作为子菜单
            if (isSubMenu(menu)) {
              parentMenu.children.push(menu)
            }
          }
        }
      })

      // sort menus and submenus
      menuMap.forEach((menu) => {
        if (menu.children.length > 0) {
          menu.children.sort((a, b) => a.sort - b.sort)
        }
      })

      return rootMenus.sort((a, b) => a.sort - b.sort)
    }
  },

  actions: {
    /**
     * setup user information
     */
    setupUserInfo(userInfo: User) {
      const {
        username,
        gender,
        birthday,
        email,
        phoneNumber,
        avatar,
        roles,
        routers,
        buttons,
        createdTime
      } = userInfo

      // use object destructuring to simplify code
      Object.assign(this, {
        username,
        gender,
        birthday,
        email,
        phoneNumber,
        avatar,
        roles,
        createdTime,
        buttons
      })

      // filter out routes without components
      this.routers = routers.filter(
        (router) =>
          router.type !== 'TEMPLATE' ||
          VIEW_MODULES[`/src/pages${router.componentPath}`]
      )
    },

    /**
     * get current user information
     */
    async me() {
      try {
        const response = await meApi()
        this.setupUserInfo(response.data)
        return response
      } catch (error) {
        return Promise.reject(error)
      }
    }
  },

  persist: {
    key: STORE_KEY,
    storage: localStorage
  }
})
