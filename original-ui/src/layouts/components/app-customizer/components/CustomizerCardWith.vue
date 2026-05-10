<script setup lang="ts">
import { useLocale } from 'vuetify'
import { cardWithOptions } from '@/constants/options'

import CustomizerLayout from '@/layouts/components/app-customizer/components/CustomizerLayout.vue'

defineOptions({
  name: 'CustomizerCardWith'
})

// composables
const { t } = useLocale()
const { cardWith } = storeToRefs(useAppStore())
const { toggleCardWith } = useAppConfig()
</script>

<template>
  <customizer-layout :title="t('$original.app.customizer.cardWith')">
    <v-item-group
      class="mb-3"
      mandatory
      :model-value="cardWith"
      @update:model-value="toggleCardWith"
    >
      <v-row>
        <v-col v-for="(item, index) in cardWithOptions" :key="index">
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
