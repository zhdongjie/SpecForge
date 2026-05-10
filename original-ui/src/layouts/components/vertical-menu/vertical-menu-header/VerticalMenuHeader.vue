<script lang="ts" setup>
import { IconX } from '@tabler/icons-vue'
import { useDisplay } from 'vuetify'
import appConfig from '@/appConfig'

defineOptions({
  name: 'VerticalMenuHeader'
})

// emits
const emits = defineEmits(['close-menu'])

// composables
const { lgAndUp } = useDisplay()
const { isVerticalMenuMini } = storeToRefs(useAppStore())

const isMouseHovered = inject<Ref<boolean>>('isMouseHovered', ref(false))
</script>

<template>
  <div
    class="d-flex align-center justify-space-between px-5 py-2 vertical-menu-header"
  >
    <div class="d-flex align-center">
      <!-- logo -->
      <v-img
        alt="logo"
        class="mr-2 sidebar-logo"
        :src="appConfig.logo"
        width="48"
      />

      <!-- name -->
      <v-slide-x-transition>
        <h2
          v-show="!isVerticalMenuMini || !lgAndUp || isMouseHovered"
          class="text-h5"
        >
          {{ appConfig.name }}
        </h2>
      </v-slide-x-transition>
    </div>

    <!-- close button -->
    <v-slide-x-transition>
      <v-btn
        v-show="!lgAndUp"
        icon
        size="small"
        variant="text"
        @click="emits('close-menu')"
      >
        <icon-x :size="16"></icon-x>
      </v-btn>
    </v-slide-x-transition>
  </div>
</template>
