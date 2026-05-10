<script setup lang="ts">
import { IconSettings } from '@tabler/icons-vue'
import { useDisplay, useLocale } from 'vuetify'

import CustomizerCardWith from '@/layouts/components/app-customizer/components/CustomizerCardWith.vue'

import CustomizerContentLayout from '@/layouts/components/app-customizer/components/CustomizerContentLayout.vue'
import CustomizerContentWidth from '@/layouts/components/app-customizer/components/CustomizerContentWidth.vue'
import CustomizerLanguage from '@/layouts/components/app-customizer/components/CustomizerLanguage.vue'
import CustomizerMenuGroupOpenOn from '@/layouts/components/app-customizer/components/CustomizerMenuGroupOpenOn.vue'
import CustomizerRouterTransition from '@/layouts/components/app-customizer/components/CustomizerRouterTransition.vue'
import CustomizerSidebarType from '@/layouts/components/app-customizer/components/CustomizerSidebarType.vue'
import CustomizerTheme from '@/layouts/components/app-customizer/components/CustomizerTheme.vue'

defineOptions({
  name: 'AppCustomizer'
})

// composables
const { t } = useLocale()
const { mobile } = useDisplay()
const route = useRoute()
const { contentLayout } = storeToRefs(useAppStore())
const currentRouterLayout = computed(() => route.meta.layout)

// state
const settingsDrawer = ref(false)
</script>

<template>
  <v-btn
    class="customizer-btn"
    color="primary"
    :icon="IconSettings"
    variant="elevated"
    @click="settingsDrawer = true"
  >
  </v-btn>
  <v-navigation-drawer
    v-model="settingsDrawer"
    class="right-sidebar"
    floating
    location="right"
    :temporary="true"
    width="320"
  >
    <div class="pa-6">
      <h3>{{ t('$original.app.customizer.settings') }}</h3>
    </div>
    <v-divider />
    <perfect-scrollbar :options="{ wheelPropagation: false }">
      <div class="pa-6">
        <!-- language -->
        <customizer-language />

        <!-- Sidebar Layout -->
        <customizer-content-layout
          v-if="currentRouterLayout == 'content' && !mobile"
        />

        <!-- Theme -->
        <customizer-theme />

        <!-- Content Width -->
        <customizer-content-width
          v-if="currentRouterLayout == 'content' && !mobile"
        />

        <!-- Sidebar Type -->
        <customizer-sidebar-type
          v-if="
            currentRouterLayout == 'content' &&
            contentLayout === 'vertical' &&
            !mobile
          "
        />

        <!-- Card With -->
        <customizer-card-with v-if="!mobile" />

        <!-- Menu Group Open On -->
        <customizer-menu-group-open-on
          v-if="
            currentRouterLayout == 'content' &&
            contentLayout === 'horizontal' &&
            !mobile
          "
        />

        <!-- Router Transition -->
        <customizer-router-transition />
      </div>
    </perfect-scrollbar>
  </v-navigation-drawer>
</template>

<style lang="scss" scoped>
.customizer-btn {
  position: fixed;
  top: calc(100vh / 3);
  right: 0;
  z-index: 1;
  border-bottom-right-radius: 2px;

  :deep(.v-icon) {
    transform-origin: center center;
    transition: all 0.2s ease-in-out;
    animation: progress-circular-rotate 1.4s linear infinite;
  }
}

.right-sidebar {
  box-shadow: 0 -1px 20px #00000014 !important;

  .ps {
    height: calc(100vh - 77px);
  }
}
</style>
