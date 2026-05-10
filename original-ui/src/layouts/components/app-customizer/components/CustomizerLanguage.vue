<script setup lang="ts">
import { useLocale } from 'vuetify'
import { languagesOptions } from '@/constants/options'

import CustomizerLayout from '@/layouts/components/app-customizer/components/CustomizerLayout.vue'

defineOptions({
  name: 'CustomizerLanguage'
})

// composables
const { t } = useLocale()
const { language } = storeToRefs(useAppStore())
const { toggleLanguage } = useAppConfig()
</script>

<template>
  <customizer-layout :title="t('$original.app.customizer.language')">
    <v-item-group
      class="mb-3"
      mandatory
      :model-value="language"
      @update:model-value="toggleLanguage"
    >
      <v-row>
        <v-col v-for="(item, index) in languagesOptions" :key="index">
          <v-item v-slot="{ isSelected, toggle }" :value="item.value">
            <v-card
              class="d-flex align-center justify-center"
              :color="isSelected ? 'primary' : undefined"
              dark
              height="48"
              :variant="isSelected ? 'tonal' : 'elevated'"
              @click="toggle"
            >
              <p class="text-caption">
                {{ t(item.label) }}
              </p>
            </v-card>
          </v-item>
        </v-col>
      </v-row>
    </v-item-group>
  </customizer-layout>
</template>
