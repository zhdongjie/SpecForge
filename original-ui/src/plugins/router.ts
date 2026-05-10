import type { App } from 'vue'

import type { PluginInstallerFn } from '@/types/original/generic'
import NProgress from 'nprogress'
import { createRouter, createWebHistory } from 'vue-router'
import { useLocale } from 'vuetify/framework'
import appConfig from '@/appConfig'
import i18n, {
  loadLocaleMessages,
  setI18nLanguage,
  SUPPORT_LOCALES,
  isSupportLanguage
} from '@/plugins/i18n'
import { addDynamicRoutes } from '@/routes/dynamicRoutes'
import routes from '@/routes/staticRoutes'

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ left: 0, top: 0 })
})

let dynamicRoutesAdded = false

router.beforeEach(async (to, from, next) => {
  NProgress.start()

  const appStore = storeToRefs(useAppStore())
  const paramsLocale = to.params.locale
  const authorizeStore = useAuthorizeStore()
  const userStore = useUserStore()
  const { current } = useLocale()

  document.title = to.meta.title
    ? `${to.meta.title} - ${appConfig.name}`
    : appConfig.name

  const isLoggedIn = authorizeStore.isLoggedIn
  const isMatchedRouter = to.matched.length

  const loginLocation = {
    name: 'authorize-login',
    replace: true,
    params: { locale: paramsLocale }
  }

  // handle locale routing - redirect to appropriate language path if needed
  if (!isSupportLanguage(paramsLocale)) {
    if (paramsLocale) {
      // if invalid locale in URL, redirect to same path with valid locale
      return next(`/${appStore.language.value}/${paramsLocale}`)
    }
    // check if the current path starts with any supported locale
    if (
      SUPPORT_LOCALES.every((locale) => !to.fullPath.startsWith(`/${locale}`))
    ) {
      // if no locale in path, add the current language to path
      return next(`/${appStore.language.value}${to.fullPath}`)
    }
  }

  // Pages required login
  if (!to.meta.public && !isLoggedIn) {
    if (!isMatchedRouter) {
      return next({
        name: 'error-404',
        params: { locale: appStore.language.value }
      })
    }
    return next(loginLocation)
  }

  if (isLoggedIn) {
    const hasUserInfo = userStore.hasUserInfo
    if (hasUserInfo && !dynamicRoutesAdded) {
      try {
        addDynamicRoutes()

        dynamicRoutesAdded = true

        // Redirect if logged in
        if (to.meta.redirectIfLoggedIn) {
          return next('/')
        }

        if (!isMatchedRouter) {
          return next({ ...to, replace: true })
        }
      } catch (error) {
        console.error(error || 'get user information failed')
        await authorizeStore.logout(false)
        return next(loginLocation)
      }
    }
  }

  if (isSupportLanguage(paramsLocale)) {
    // load locale messages
    if (!i18n.global.availableLocales.includes(paramsLocale)) {
      await loadLocaleMessages(paramsLocale)
    }

    // set i18n language
    setI18nLanguage(paramsLocale)

    // set vuetify language
    current.value = paramsLocale

    if (appStore.language.value !== paramsLocale && isLoggedIn) {
      await userStore.me()
    }

    // set store language
    appStore.language.value = paramsLocale
  }

  return next()
})

router.afterEach(() => {
  NProgress.done()
})

router.onError(() => {
  NProgress.done()
})

export default router

export const install: PluginInstallerFn = async (app: App<Element>) => {
  app.use(router)
}
