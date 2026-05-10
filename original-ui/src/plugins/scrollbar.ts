import type { App } from 'vue'
import type { PluginInstallerFn } from '@/types/original/generic'
import { PerfectScrollbarPlugin } from 'vue3-perfect-scrollbar'

export const install: PluginInstallerFn = (app: App<Element>) => {
  app.use(PerfectScrollbarPlugin)
}
