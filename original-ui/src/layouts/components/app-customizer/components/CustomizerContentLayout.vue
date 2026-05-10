<script lang="ts" setup>
import { useLocale } from 'vuetify'
import { contentLayoutOptions } from '@/constants/options'

import CustomizerLayout from '@/layouts/components/app-customizer/components/CustomizerLayout.vue'

defineOptions({
  name: 'CustomizerContentLayout'
})

// composables
const { contentLayout } = storeToRefs(useAppStore())
const { toggleContentLayout } = useAppConfig()
const { t } = useLocale()
</script>

<template>
  <customizer-layout :title="t('$original.app.customizer.sidebarLayout')">
    <v-item-group
      class="mb-3"
      mandatory
      :model-value="contentLayout"
      :multiple="false"
      @update:model-value="toggleContentLayout"
    >
      <v-row>
        <v-col v-for="item in contentLayoutOptions" :key="item.value">
          <v-item v-slot="{ isSelected, toggle }" :value="item.value">
            <v-card
              class="d-flex align-center justify-center"
              dark
              height="48"
              @click="toggle"
            >
              <v-icon
                class="mr-1"
                :color="isSelected ? 'primary' : undefined"
                :icon="item.icon"
                size="small"
              ></v-icon>
            </v-card>
          </v-item>
        </v-col>
      </v-row>
    </v-item-group>
  </customizer-layout>
</template>
