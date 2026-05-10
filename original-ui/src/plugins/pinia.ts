import type { App } from 'vue'
import type { PluginInstallerFn } from '@/types/original/generic'
import piniaPluginPersistedState from 'pinia-plugin-persistedstate'

const pinia = createPinia()

pinia.use(piniaPluginPersistedState)

export default pinia

export const install: PluginInstallerFn = (app: App<Element>) => {
  app.use(pinia)
}
