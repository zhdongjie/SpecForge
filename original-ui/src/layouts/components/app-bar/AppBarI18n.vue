<script setup lang="ts">
import { IconLanguage } from '@tabler/icons-vue'
import { useLocale } from 'vuetify'
import { languagesOptions } from '@/constants/options'

defineOptions({ name: 'AppBarI18n' })

// composables
const { t } = useLocale()
const { language } = storeToRefs(useAppStore())
const { toggleLanguage } = useAppConfig()

// methods
const currentLanguageLabel = computed(() => {
  const item = languagesOptions.find((i) => i.value === language.value)
  return item ? t(item.label) : language.value
})
</script>

<template>
  <v-menu
    class="app-bar-tools"
    location="bottom center"
    transition="slide-y-transition"
  >
    <template #activator="{ props }">
      <v-btn v-bind="props">
        <icon-language :size="18" />
        <span class="ms-2 text-caption">
          {{ currentLanguageLabel }}
        </span>
      </v-btn>
    </template>

    <v-list density="compact" :lines="false" :nav="true">
      <v-list-item
        v-for="item in languagesOptions"
        :key="item.value"
        :active="item.value === language"
        color="primary"
        :value="item.value"
        @click="toggleLanguage(item.value)"
      >
        <v-list-item-title class="text-caption">
          {{ t(item.label) }}
        </v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>
