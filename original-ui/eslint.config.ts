import { fileURLToPath } from 'node:url'
import { includeIgnoreFile } from '@eslint/compat'
import eslint from '@eslint/js'
// import vuetify from 'eslint-config-vuetify'
import eslintPluginPrettierRecommended from 'eslint-plugin-prettier/recommended'
import eslintPluginVue from 'eslint-plugin-vue'
import globals from 'globals'
import tsEslint from 'typescript-eslint'
import autoImport from './.eslintrc-auto-import.json'

const gitignorePath = fileURLToPath(new URL('.gitignore', import.meta.url))

export default tsEslint.config(
  includeIgnoreFile(gitignorePath),
  eslint.configs.recommended,
  tsEslint.configs.recommended,
  eslintPluginVue.configs['flat/recommended'],
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...autoImport.globals
      }
    }
  },

  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tsEslint.parser,
        ecmaFeatures: {
          jsx: true
        }
      }
    },
    rules: {
      'vue/multi-word-component-names': 'off'
    }
  },

  {
    files: ['**/*.{ts,tsx,vue}'],
    rules: {}
  },

  // await vuetify(),

  eslintPluginPrettierRecommended
)
