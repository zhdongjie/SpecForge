<script setup lang="ts">
import { useLocale } from 'vuetify'
import { contentWidthOptions } from '@/constants/options'

import CustomizerLayout from '@/layouts/components/app-customizer/components/CustomizerLayout.vue'

defineOptions({
  name: 'CustomizerContentWidth'
})

// composables
const { t } = useLocale()
const { contentWidth } = storeToRefs(useAppStore())
const { toggleContentWidth } = useAppConfig()
</script>

<template>
  <customizer-layout :title="t('$original.app.customizer.contentWidth')">
    <v-item-group
      class="mb-3"
      mandatory
      :model-value="contentWidth"
      @update:model-value="toggleContentWidth"
    >
      <v-row>
        <v-col v-for="(item, index) in contentWidthOptions" :key="index">
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
