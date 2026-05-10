<script lang="ts" setup>
import { IconArrowsMinimize, IconMaximize } from '@tabler/icons-vue'

defineOptions({
  name: 'AppBarFullscreen'
})

// composables
const { isFullscreen, toggle, isSupported } = useFullscreen()
</script>

<template>
  <v-btn
    v-show="isSupported"
    class="app-bar-tools"
    icon
    size="small"
    @click="toggle"
  >
    <icon-arrows-minimize v-if="isFullscreen" :size="18" />
    <icon-maximize v-else :size="18" />
  </v-btn>
</template>
