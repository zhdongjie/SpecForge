<script lang="ts" setup>
import type { SubheaderMenu } from '@/types/original/menu'
import { IconDots } from '@tabler/icons-vue'
import { useDisplay } from 'vuetify'

import VerticalMenuGroup from '@/layouts/components/vertical-menu/vertical-menu-group/VerticalMenuGroup.vue'

import VerticalMenuLink from '@/layouts/components/vertical-menu/vertical-menu-link/VerticalMenuLink.vue'
import useVerticalMenu from '@/layouts/composables/vertical-menu/useVerticalMenu'

defineOptions({
  name: 'VerticalMenuSubheader',
  components: {
    VerticalMenuLink,
    VerticalMenuGroup
  }
})

// props
defineProps({
  item: {
    type: Object as PropType<SubheaderMenu>,
    required: true
  }
})

// composables
const { lgAndUp } = useDisplay()
const { resolveItemComponent } = useVerticalMenu()
const { isVerticalMenuMini } = storeToRefs(useAppStore())

const showSubheader = computed(
  () =>
    // 'not mini menu'
    // or 'screen < lg'
    // or 'is mini menu and mouse hovered'
    !isVerticalMenuMini.value ||
    !lgAndUp.value ||
    (isVerticalMenuMini.value && isMouseHovered.value)
)

const showDotsIcon = computed(
  () => isVerticalMenuMini.value && !isMouseHovered.value && lgAndUp.value
)

const isMouseHovered = inject<Ref<boolean>>('isMouseHovered', ref(false))
</script>

<template>
  <div class="vertical-menu-subheader">
    <!-- subheader -->
    <div v-show="showSubheader">
      <p class="sidebar-subheader">
        {{ item.name }}
      </p>
    </div>

    <!-- dots icon -->
    <div v-show="showDotsIcon" class="dots-icon">
      <icon-dots :size="16" stroke-width="1.5"></icon-dots>
    </div>
  </div>

  <!-- menu group items -->
  <component
    :is="resolveItemComponent(child)"
    v-for="child in item.children"
    :key="child.id"
    :item="child"
  ></component>
</template>
