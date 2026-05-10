import type { Language, Theme } from '@/types/original/config'
import { useTheme } from 'vuetify'

export const useAppConfig = () => {
  const appStore = storeToRefs(useAppStore())
  const route = useRoute()
  const vuetifyTheme = useTheme()

  const createSetter =
    <T>(refObj: Ref<T>) =>
    (val: T) => {
      refObj.value = val
    }

  const toggleLanguage = (targetLanguage: Language) => {
    const originalLanguage = appStore.language.value
    if (originalLanguage !== targetLanguage) {
      const targetPath = route.fullPath.replace(
        originalLanguage,
        targetLanguage
      )

      window.location.href = `${window.location.origin}${targetPath}`
    }
  }

  const toggleTheme = (targetTheme: Theme) => {
    appStore.theme.value = targetTheme
    vuetifyTheme.global.name.value = targetTheme
  }

  return {
    toggleLanguage,
    toggleTheme,
    toggleContentLayout: createSetter(appStore.contentLayout),
    toggleContentWidth: createSetter(appStore.contentWidth),
    toggleIsVerticalMenuMini: createSetter(appStore.isVerticalMenuMini),
    toggleCardWith: createSetter(appStore.cardWith),
    toggleHorizontalMenuGroupOpenOnHover: createSetter(
      appStore.horizontalMenuGroupOpenOnHover
    ),
    toggleRouterTransition: createSetter(appStore.routerTransition)
  }
}
