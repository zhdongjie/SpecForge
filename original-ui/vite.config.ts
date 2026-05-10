import { fileURLToPath, URL } from 'node:url'
import VueI18n from '@intlify/unplugin-vue-i18n/vite'

import Vue from '@vitejs/plugin-vue'
import VueJsx from '@vitejs/plugin-vue-jsx'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { defineConfig } from 'vite'
import VueDevTools from 'vite-plugin-vue-devtools'
import Vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

// https://vite.dev/config/
const vite = () => {
  return defineConfig({
    server: {
      host: '0.0.0.0',
      port: 3000,
      open: true
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('src', import.meta.url))
      }
    },
    plugins: [
      Vue({
        template: { transformAssetUrls }
      }),

      VueJsx(),

      // https://github.com/vuetifyjs/vuetify-loader/tree/master/packages/vite-plugin#readme
      Vuetify({
        autoImport: true,
        styles: {
          configFile: 'src/styles/vuetify/settings.scss'
        }
      }),

      // https://github.com/intlify/bundle-tools/tree/main/packages/unplugin-vue-i18n
      VueI18n({
        include: [fileURLToPath(new URL('src/locales/**', import.meta.url))]
      }),

      // https://github.com/antfu/unplugin-auto-import
      AutoImport({
        imports: ['vue', 'vue-router', 'pinia', 'vue-i18n', '@vueuse/core'],
        dirs: ['src/composables', 'src/stores'],
        dts: 'src/types/auto-import.d.ts',
        vueTemplate: true,
        eslintrc: { enabled: true }
      }),

      // https://github.com/antfu/unplugin-vue-components
      Components({
        dts: 'src/types/components.d.ts'
      }),

      // https://github.com/webfansplz/vite-plugin-vue-devtools
      VueDevTools()
    ]
  })
}

export default vite
