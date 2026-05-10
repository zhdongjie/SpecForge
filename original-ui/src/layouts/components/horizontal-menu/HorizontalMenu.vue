<script lang="ts" setup>
import HorizontalMenuHeaderGroup from '@/layouts/components/horizontal-menu/components/horizontal-menu-header-group/HorizontalMenuHeaderGroup.vue'

import HorizontalMenuHeaderLink from '@/layouts/components/horizontal-menu/components/horizontal-menu-header-link/HorizontalMenuHeaderLink.vue'

import useHorizontalMenu from '@/layouts/composables/horizontal-menu/useHorizontalMenu'

defineOptions({
  name: 'HorizontalMenu',
  components: {
    HorizontalMenuHeaderLink,
    HorizontalMenuHeaderGroup
  }
})

// composables
const { resolveHeaderComponent } = useHorizontalMenu()
const userStore = useUserStore()
const menuItems = userStore.getMenus
</script>

<template>
  <div
    class="d-flex align-center position-relative border-bottom horizontal-menu"
  >
    <!-- header items -->
    <component
      :is="resolveHeaderComponent(item)"
      v-for="item in menuItems"
      :key="item.id"
      :item="item"
    />
  </div>
</template>
