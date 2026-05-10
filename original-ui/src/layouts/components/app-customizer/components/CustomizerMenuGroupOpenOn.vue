<script setup lang="ts">
import { useLocale } from 'vuetify'
import { menuGroupOpenOnOptions } from '@/constants/options'

import CustomizerLayout from '@/layouts/components/app-customizer/components/CustomizerLayout.vue'

defineOptions({
  name: 'CustomizerMenuGroupOpenOn'
})

// composables
const { t } = useLocale()
const { horizontalMenuGroupOpenOnHover } = storeToRefs(useAppStore())
const { toggleHorizontalMenuGroupOpenOnHover } = useAppConfig()
</script>

<template>
  <customizer-layout :title="t('$original.app.customizer.menuGroupOpenOn')">
    <v-item-group
      class="mb-3"
      mandatory
      :model-value="horizontalMenuGroupOpenOnHover"
      @update:model-value="toggleHorizontalMenuGroupOpenOnHover"
    >
      <v-row>
        <v-col v-for="(item, index) in menuGroupOpenOnOptions" :key="index">
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
