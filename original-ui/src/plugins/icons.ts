import type { App } from 'vue'
import type { PluginInstallerFn } from '@/types/original/generic'
import * as tabler from '@tabler/icons-vue'

export const install: PluginInstallerFn = (app: App<Element>) => {
  for (const [name, component] of Object.entries(tabler)) {
    app.component(name, component as Component)
  }
}
