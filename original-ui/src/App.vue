<script lang="ts" setup>
import { VSonner } from 'vuetify-sonner'
import AppCustomizer from '@/layouts/components/app-customizer/AppCustomizer.vue'

import useLayout from '@/layouts/composables/useLayout'

import LayoutBlank from '@/layouts/variant/blank/LayoutBlank.vue'
import LayoutContentHorizontal from '@/layouts/variant/content/horizontal/LayoutContentHorizontal.vue'
import LayoutContentVertical from '@/layouts/variant/content/vertical/LayoutContentVertical.vue'

defineOptions({
  name: 'App',
  components: {
    LayoutBlank,
    LayoutContentVertical,
    LayoutContentHorizontal
  }
})

// composable
const route = useRoute()
const { contentLayout, routerTransition, theme } = storeToRefs(useAppStore())
const { toggleTheme } = useAppConfig()
const { breakpointLayoutToggle } = useLayout()

// mounted
onMounted(() => {
  // setup theme
  toggleTheme(theme.value)
})

// layout toggle
breakpointLayoutToggle()

// methods
const resolveLayoutVariant = computed(() => {
  const currentRouterLayout = route.meta.layout

  let layout = `layout-${currentRouterLayout}`

  if (currentRouterLayout === 'content') {
    layout = `${layout}-${contentLayout.value}`
  }

  return layout
})
</script>

<template>
  <v-app class="original-app">
    <VSonner :offset="24" position="top-right" />
    <app-customizer />
    <component :is="resolveLayoutVariant">
      <router-view v-slot="{ Component }">
        <transition appear mode="out-in" :name="routerTransition">
          <component :is="Component" />
        </transition>
      </router-view>
    </component>
  </v-app>
</template>
