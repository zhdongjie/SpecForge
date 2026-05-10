import type { App } from 'vue'
import type { Language } from '@/types/original/config'

import type { PluginInstallerFn } from '@/types/original/generic'
import { createI18n } from 'vue-i18n'
import { en, zhHans } from 'vuetify/locale'
import request from '@/plugins/axios'

const i18n = createI18n({
  legacy: false,
  locale: '',
  messages: {}
})

const localesMap = Object.fromEntries(
  Object.entries(
    import.meta.glob('@/locales/*.json', { import: 'default' })
  ).map(([path, loadLocale]) => [path.match(/([\w-]*)\.json/)?.[1], loadLocale])
) as Record<Language, () => Promise<Record<string, unknown>>>

export const SUPPORT_LOCALES = Object.keys(localesMap) as Language[]

export function isSupportLanguage(locale: unknown): locale is Language {
  return SUPPORT_LOCALES.includes(locale as Language)
}

export const setI18nLanguage = (language: Language) => {
  i18n.global.locale.value = language

  /**
   * NOTE:
   * If you need to specify the language setting for headers, such as the `fetch` API, set it here.
   * The following is an example for axios.
   *
   * axios.defaults.headers.common['Accept-Language'] = language
   */
  request.instance.defaults.headers.common['Accept-Language'] = language

  if (document) {
    document.querySelector('html')?.setAttribute('lang', language)
  }
}

const vuetifyLangMap: Record<Language, unknown> = {
  'en-US': en,
  'zh-CN': zhHans
}

export const loadLocaleMessages = async (language: Language) => {
  // load locale messages with dynamic import
  const customMessages = await localesMap[language]()
  const vuetifyMessages = vuetifyLangMap[language] || {}

  const messages = {
    $vuetify: vuetifyMessages,
    $original: customMessages
  }

  i18n.global.setLocaleMessage(language, messages)

  return nextTick()
}

export default i18n

export const install: PluginInstallerFn = (app: App<Element>) => {
  app.use(i18n)
}
