<script lang="ts" setup>
import { useDisplay } from 'vuetify'

defineOptions({
  name: 'LayoutBlank'
})

// composables
const { cardWith } = storeToRefs(useAppStore())
const { mobile } = useDisplay()
</script>

<template>
  <div class="layout-blank">
    <v-main>
      <div :class="{ 'card-border': cardWith === 'border' && !mobile }">
        <slot />
      </div>
    </v-main>
  </div>
</template>
