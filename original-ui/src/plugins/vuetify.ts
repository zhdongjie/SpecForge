import type { App } from 'vue'
import type { PluginInstallerFn } from '@/types/original/generic'
import { createVuetify } from 'vuetify'
import { VDateInput } from 'vuetify/labs/VDateInput'
import { createVueI18nAdapter } from 'vuetify/locale/adapters/vue-i18n'
import appConfig from '@/appConfig'
import i18n from '@/plugins/i18n'

const vuetify = createVuetify({
  locale: {
    adapter: createVueI18nAdapter({ i18n, useI18n })
  },
  components: {
    VDateInput
  },
  defaults: {
    VList: {
      density: 'compact'
    },
    VSelect: {
      baseColor: 'input-border'
    }
  },
  theme: {
    defaultTheme: appConfig.theme,
    themes: {
      'dark-orange': {
        dark: true,
        variables: {
          'border-color': '#333F55',
          'text-secondary': '#7C8FAC',
          'border-opacity': 0.6
        },
        colors: {
          background: '#171C23',
          surface: '#171C23',
          primary: '#FB9678',
          'on-primary': '#FFFFFF',
          secondary: '#03C9D7',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#13DEB9',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF',
          'input-border': '#465670'
        }
      },
      'dark-blue': {
        dark: true,
        variables: {
          'border-color': '#333F55',
          'text-secondary': '#7C8FAC',
          'border-opacity': 0.6
        },
        colors: {
          background: '#2A3447',
          surface: '#2A3447',
          primary: '#1E4DB7',
          'on-primary': '#FFFFFF',
          secondary: '#1A97F5',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF',
          'input-border': '#465670'
        }
      },
      'dark-red': {
        dark: true,
        variables: {
          'border-color': '#333F55',
          'text-secondary': '#7C8FAC',
          'border-opacity': 0.6
        },
        colors: {
          background: '#171C23',
          surface: '#171C23',
          primary: '#5E244D',
          'on-primary': '#FFFFFF',
          secondary: '#FF5C8E',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF',
          'input-border': '#465670'
        }
      },
      'dark-purple': {
        dark: true,
        variables: {
          'border-color': '#333F55',
          'text-secondary': '#7C8FAC',
          'border-opacity': 0.6
        },
        colors: {
          background: '#171C23',
          surface: '#171C23',
          primary: '#402E8D',
          'on-primary': '#FFFFFF',
          secondary: '#9B52FF',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF',
          'input-border': '#465670'
        }
      },
      'dark-green': {
        dark: true,
        variables: {
          'border-color': '#333F55',
          'text-secondary': '#7C8FAC',
          'border-opacity': 0.6
        },
        colors: {
          background: '#171C23',
          surface: '#171C23',
          primary: '#066A9B',
          'on-primary': '#FFFFFF',
          secondary: '#00CEC3',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF',
          'input-border': '#465670'
        }
      },
      'dark-indigo': {
        dark: true,
        variables: {
          'border-color': '#333F55',
          'text-secondary': '#7C8FAC',
          'border-opacity': 0.6
        },
        colors: {
          background: '#171C23',
          surface: '#171C23',
          primary: '#11397B',
          'on-primary': '#FFFFFF',
          secondary: '#1E4DB7',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF',
          'input-border': '#465670'
        }
      },
      'light-orange': {
        dark: false,
        variables: {
          'border-color': '#E5EAEF',
          'border-opacity': 0.6
        },
        colors: {
          background: '#F6F6F6',
          surface: '#FFFFFF',
          primary: '#FB9678',
          'on-primary': '#FFFFFF',
          secondary: '#03C9D7',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#13DEB9',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF'
        }
      },
      'light-blue': {
        dark: false,
        variables: {
          'border-color': '#E5EAEF',
          'border-opacity': 0.6
        },
        colors: {
          background: '#F6F6F6',
          surface: '#FFFFFF',
          primary: '#1E4DB7',
          'on-primary': '#FFFFFF',
          secondary: '#1A97F5',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF'
        }
      },
      'light-red': {
        dark: false,
        variables: {
          'border-color': '#E5EAEF',
          'border-opacity': 0.6
        },
        colors: {
          background: '#F6F6F6',
          surface: '#FFFFFF',
          primary: '#5E244D',
          'on-primary': '#FFFFFF',
          secondary: '#FF5C8E',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF'
        }
      },
      'light-purple': {
        dark: false,
        variables: {
          'border-color': '#E5EAEF',
          'border-opacity': 0.6
        },
        colors: {
          background: '#F6F6F6',
          surface: '#FFFFFF',
          primary: '#402E8D',
          'on-primary': '#FFFFFF',
          secondary: '#9B52FF',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF'
        }
      },
      'light-green': {
        dark: false,
        variables: {
          'border-color': '#E5EAEF',
          'border-opacity': 0.6
        },
        colors: {
          background: '#F6F6F6',
          surface: '#FFFFFF',
          primary: '#066A9B',
          'on-primary': '#FFFFFF',
          secondary: '#00CEC3',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF'
        }
      },
      'light-indigo': {
        dark: false,
        variables: {
          'border-color': '#E5EAEF',
          'border-opacity': 0.6
        },
        colors: {
          background: '#F6F6F6',
          surface: '#FFFFFF',
          primary: '#11397B',
          'on-primary': '#FFFFFF',
          secondary: '#1E4DB7',
          'on-secondary': '#FFFFFF',
          error: '#FA896B',
          'on-error': '#FFFFFF',
          info: '#539BFF',
          'on-info': '#FFFFFF',
          success: '#05B187',
          'on-success': '#FFFFFF',
          warning: '#FFAE1F',
          'on-warning': '#FFFFFF'
        }
      }
    }
  }
})

export default vuetify

export const install: PluginInstallerFn = (app: App<Element>) => {
  app.use(vuetify)
}
