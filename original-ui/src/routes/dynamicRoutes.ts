import type { RouteRecordRaw } from 'vue-router'
import router from '@/plugins/router'

const fallback404Route: RouteRecordRaw = {
  path: ':pathMatch(.*)*',
  meta: {
    title: 'fallback-404-route',
    layout: 'content',
    dynamic: true
  },
  redirect: { name: 'error-404' }
}

export const addDynamicRoutes = () => {
  const userStore = useUserStore()

  const dynamicRoutes = userStore.getRouters

  for (const dynamicRoute of dynamicRoutes) {
    router.addRoute('locale', dynamicRoute)
  }

  router.addRoute('locale', fallback404Route)
}

export const resetDynamicRoutes = () => {
  for (const route of router.getRoutes()) {
    if (route.meta?.dynamic && route.name && router.hasRoute(route.name)) {
      router.removeRoute(route.name)
    }
  }
}
