<script lang="ts" setup>
import type { Theme } from '@/types/original/config'
import { IconMoonStars, IconSun } from '@tabler/icons-vue'
import { useTheme } from 'vuetify'

defineOptions({ name: 'AppBarTheme' })

// composables
const { toggleTheme } = useAppConfig()
const { global: vuetifyTheme } = useTheme()
const { theme: configTheme } = storeToRefs(useAppStore())

// computed
const isDark = computed(() => configTheme.value.startsWith('dark'))

const toTheme = (themeStr: string): Theme => {
  if (
    [
      'dark-orange',
      'dark-blue',
      'dark-red',
      'dark-purple',
      'dark-green',
      'dark-indigo',
      'light-orange',
      'light-blue',
      'light-red',
      'light-purple',
      'light-green',
      'light-indigo'
    ].includes(themeStr)
  ) {
    return themeStr as Theme
  }
  return 'light-orange'
}

// methods
const getToggleTheme = (): Theme => {
  return vuetifyTheme.current.value.dark
    ? toTheme(configTheme.value.replace(/^dark/, 'light'))
    : toTheme(configTheme.value.replace(/^light/, 'dark'))
}
</script>

<template>
  <v-btn
    class="app-bar-tools"
    icon
    size="small"
    @click="toggleTheme(getToggleTheme())"
  >
    <v-fade-transition mode="out-in">
      <icon-moon-stars v-if="isDark" key="dark" :size="18" />
      <icon-sun v-else key="light" :size="18" />
    </v-fade-transition>
  </v-btn>
</template>
