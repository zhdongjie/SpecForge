<script setup lang="ts">
import { useDisplay } from 'vuetify'

defineOptions({
  name: 'AppContentContainer'
})

// composables
const { contentWidth, cardWith } = storeToRefs(useAppStore())
const { mobile } = useDisplay()
</script>

<template>
  <div
    class="app-content-container mx-auto"
    :class="{
      'card-border': cardWith === 'border' && !mobile,
      'app-content-container-boxed': contentWidth === 'boxed'
    }"
  >
    <slot></slot>
  </div>
</template>
