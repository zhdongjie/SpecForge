<script setup lang="ts">
import VerticalMenuGroup from '@/layouts/components/vertical-menu/vertical-menu-group/VerticalMenuGroup.vue'

import VerticalMenuHeader from '@/layouts/components/vertical-menu/vertical-menu-header/VerticalMenuHeader.vue'

import VerticalMenuLink from '@/layouts/components/vertical-menu/vertical-menu-link/VerticalMenuLink.vue'
import VerticalMenuSubheader from '@/layouts/components/vertical-menu/vertical-menu-subheader/VerticalMenuSubheader.vue'
import useVerticalMenu from '@/layouts/composables/vertical-menu/useVerticalMenu'

defineOptions({
  name: 'VerticalMenu',
  components: {
    VerticalMenuSubheader,
    VerticalMenuLink,
    VerticalMenuGroup
  }
})

// emits
const emits = defineEmits(['close-menu'])

// states
const openGroups = ref([])

// mounted
onMounted(() => {
  if (isVerticalMenuMini.value) openGroups.value = []
})

// composables
const { isMouseHovered, resolveItemComponent } = useVerticalMenu()
const userStore = useUserStore()
const { isVerticalMenuMini } = storeToRefs(useAppStore())

const menuItems = userStore.getMenus

provide('openGroups', openGroups)
provide('isMouseHovered', isMouseHovered)
</script>

<template>
  <div
    class="vertical-menu"
    @mouseenter="isMouseHovered = true"
    @mouseleave="isMouseHovered = false"
  >
    <!-- sidebar header -->
    <slot name="vertical-menu-header">
      <vertical-menu-header @close-menu="emits('close-menu')" />
    </slot>

    <!-- sidebar menus -->
    <perfect-scrollbar :options="{ wheelPropagation: false }">
      <div class="vertical-menu-items">
        <v-list v-model:opened="openGroups" density="compact" :nav="true">
          <component
            :is="resolveItemComponent(item)"
            v-for="item in menuItems"
            :key="item.id"
            :item="item"
          />
        </v-list>
      </div>
    </perfect-scrollbar>
  </div>
</template>
