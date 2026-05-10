<script setup lang="ts">
import { IconCheck } from '@tabler/icons-vue'
import { useLocale } from 'vuetify'
import { themeOptions } from '@/constants/options'

import CustomizerLayout from '@/layouts/components/app-customizer/components/CustomizerLayout.vue'

defineOptions({
  name: 'CustomizerTheme'
})

// composables
const { t } = useLocale()
const { theme: themeConfig } = storeToRefs(useAppStore())
const { toggleTheme } = useAppConfig()
</script>

<template>
  <div class="customizer-theme">
    <v-item-group
      mandatory
      :model-value="themeConfig"
      @update:model-value="toggleTheme"
    >
      <customizer-layout
        v-for="(theme, index) in themeOptions"
        :key="index"
        :title="t(theme.title)"
      >
        <v-row>
          <v-col v-for="item in theme.items" :key="item.value" :cols="4">
            <v-item v-slot="{ isSelected, toggle }" :value="item.value">
              <v-card
                class="d-flex align-center justify-center"
                height="48"
                @click="toggle"
              >
                <v-avatar :color="item.color" size="24">
                  <v-icon
                    v-if="isSelected"
                    class="text-white"
                    :icon="IconCheck"
                    size="16"
                  ></v-icon>
                </v-avatar>
              </v-card>
            </v-item>
          </v-col>
        </v-row>
      </customizer-layout>
    </v-item-group>
  </div>
</template>
