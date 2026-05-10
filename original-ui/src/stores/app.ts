import type { App } from '@/types/original/store'
import appConfig from '@/appConfig'

const STORE_KEY = 'original-app'

/**
 * app store for managing application settings and preferences
 */
export const useAppStore = defineStore(STORE_KEY, {
  state: (): App => ({
    language: appConfig.language,
    theme: appConfig.theme,
    contentLayout: appConfig.contentLayout,
    contentWidth: appConfig.contentWidth,
    cardWith: appConfig.cardWith,
    isVerticalMenuMini: appConfig.isVerticalMenuMini,
    isVerticalMenuAccordion: appConfig.isVerticalMenuAccordion,
    horizontalMenuGroupOpenOnHover: appConfig.horizontalMenuGroupOpenOnHover,
    routerTransition: appConfig.routerTransition
  }),

  getters: {},

  actions: {},

  persist: {
    key: STORE_KEY,
    storage: localStorage
  }
})
