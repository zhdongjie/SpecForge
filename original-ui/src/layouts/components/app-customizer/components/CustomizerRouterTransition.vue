<script setup lang="ts">
import { IconEaseOutControlPoint } from '@tabler/icons-vue'
import { useLocale } from 'vuetify'
import { routerTransitionOptions } from '@/constants/options'

import CustomizerLayout from '@/layouts/components/app-customizer/components/CustomizerLayout.vue'

defineOptions({
  name: 'CustomizerRouterTransition'
})

// composables
const { t } = useLocale()
const { routerTransition } = storeToRefs(useAppStore())
const { toggleRouterTransition } = useAppConfig()
</script>

<template>
  <customizer-layout :title="t('$original.app.customizer.routerTransition')">
    <v-select
      v-model="routerTransition"
      base-color="input-border"
      color="primary"
      density="comfortable"
      hide-details
      :items="routerTransitionOptions"
      :list-props="{ nav: true, density: 'compact' }"
      variant="outlined"
      @update:model-value="toggleRouterTransition"
    >
      <template #prepend-inner>
        <v-icon :icon="IconEaseOutControlPoint" size="x-small"></v-icon>
      </template>
    </v-select>
  </customizer-layout>
</template>
