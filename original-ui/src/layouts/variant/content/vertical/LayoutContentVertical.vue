<script lang="ts" setup>
import { IconMenu2 } from '@tabler/icons-vue'
import { useDisplay } from 'vuetify'

import AppBarFullscreen from '@/layouts/components/app-bar/AppBarFullscreen.vue'
import AppBarI18n from '@/layouts/components/app-bar/AppBarI18n.vue'
import AppBarTheme from '@/layouts/components/app-bar/AppBarTheme.vue'
import AppBarUserMenu from '@/layouts/components/app-bar/AppBarUserMenu.vue'
import AppBreadcrumbs from '@/layouts/components/app-breadcrumbs/AppBreadcrumbs.vue'
import AppContentContainer from '@/layouts/components/app-content-container/AppContentContainer.vue'

import VerticalMenu from '@/layouts/components/vertical-menu/VerticalMenu.vue'

defineOptions({
  name: 'LayoutContentVertical'
})

// states
const isVerticalMenuActive = ref(true)

// composables
const { lgAndUp } = useDisplay()
const { isVerticalMenuMini } = storeToRefs(useAppStore())

// methods
const handlerToggleVerticaMenu = () => {
  if (lgAndUp.value) {
    isVerticalMenuMini.value = !isVerticalMenuMini.value
  } else {
    isVerticalMenuActive.value = !isVerticalMenuActive.value
  }
}

// watch
watch(
  () => lgAndUp.value,
  (value) => {
    isVerticalMenuActive.value = value
    if (!lgAndUp.value) {
      isVerticalMenuMini.value = false
    }
  },
  {
    immediate: true
  }
)
</script>

<template>
  <div class="layout-content-vertical">
    <v-navigation-drawer
      v-model="isVerticalMenuActive"
      class="left-sidebar"
      :expand-on-hover="isVerticalMenuMini"
      floating
      :rail="isVerticalMenuMini && lgAndUp"
      rail-width="76"
    >
      <vertical-menu @close-menu="isVerticalMenuActive = false" />
    </v-navigation-drawer>

    <v-app-bar color="background" :flat="true">
      <v-app-bar-nav-icon @click="handlerToggleVerticaMenu">
        <icon-menu2 :size="20"></icon-menu2>
      </v-app-bar-nav-icon>

      <!-- breadcrumbs -->
      <app-breadcrumbs :show-icon="false"></app-breadcrumbs>

      <!-- spacer -->
      <v-spacer></v-spacer>

      <!-- fullscreen -->
      <app-bar-fullscreen></app-bar-fullscreen>

      <!-- i18n -->
      <app-bar-i18n></app-bar-i18n>

      <!-- theme -->
      <app-bar-theme></app-bar-theme>

      <!-- user menu -->
      <app-bar-user-menu></app-bar-user-menu>
    </v-app-bar>

    <v-main>
      <v-container>
        <app-content-container>
          <slot />
        </app-content-container>
      </v-container>
    </v-main>

    <!-- footer -->
    <v-footer :absolute="true" :app="true" />
  </div>
</template>
