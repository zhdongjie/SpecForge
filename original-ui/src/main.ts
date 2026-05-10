import type { PluginInstallerFn } from '@/types/original/generic'
import App from '@/App.vue'
import '@/styles/main.scss'

const app = createApp(App)

// install plugins
for (const m of Object.values(
  import.meta.glob<{ install: PluginInstallerFn }>('@/plugins/*.ts', {
    eager: true
  })
)) {
  m.install?.(app)
}

app.mount('#app')
