<script lang="ts" setup>
import appConfig from '@/appConfig'

import AppBarFullscreen from '@/layouts/components/app-bar/AppBarFullscreen.vue'
import AppBarI18n from '@/layouts/components/app-bar/AppBarI18n.vue'
import AppBarTheme from '@/layouts/components/app-bar/AppBarTheme.vue'
import AppBarUserMenu from '@/layouts/components/app-bar/AppBarUserMenu.vue'
import AppBreadcrumbs from '@/layouts/components/app-breadcrumbs/AppBreadcrumbs.vue'

import AppContentContainer from '@/layouts/components/app-content-container/AppContentContainer.vue'
import HorizontalMenu from '@/layouts/components/horizontal-menu/HorizontalMenu.vue'

defineOptions({
  name: 'LayoutContentHorizontal'
})
</script>

<template>
  <div class="layout-content-horizontal">
    <v-app-bar color="background" :flat="true">
      <v-container class="py-0">
        <app-content-container>
          <div class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <!-- logo -->
              <v-img
                alt="logo"
                class="mr-2"
                :src="appConfig.logo"
                :width="60"
              />

              <!-- name -->
              <h2 class="text-h4">{{ appConfig.name }}</h2>
            </div>

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
          </div>
        </app-content-container>
      </v-container>
    </v-app-bar>

    <div class="bg-surface">
      <v-container class="py-0">
        <app-content-container>
          <horizontal-menu></horizontal-menu>
        </app-content-container>
      </v-container>
    </div>

    <!-- content -->
    <v-main>
      <v-container>
        <app-content-container>
          <app-breadcrumbs></app-breadcrumbs>
          <slot></slot>
        </app-content-container>
      </v-container>
    </v-main>

    <!-- footer -->
    <v-footer :absolute="true" :app="true">
      <v-container class="py-0">
        <app-content-container></app-content-container>
      </v-container>
    </v-footer>
  </div>
</template>
