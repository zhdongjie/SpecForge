<script lang="ts" setup>
import type { LinkMenu, TemplateMenu } from '@/types/original/menu'
import appConfig from '@/appConfig'
import useMenuLink from '@/layouts/composables/useMenuLink'

defineOptions({
  name: 'VerticalMenuLink'
})

// props
const componentProps = defineProps({
  item: {
    type: Object as PropType<TemplateMenu | LinkMenu>,
    required: true
  }
})

// composables
const propsRefs = toRefs(componentProps)
const { isVerticalMenuMini } = storeToRefs(useAppStore())
const { linkProps, isActive } = useMenuLink(propsRefs.item.value)

const isMouseHovered = inject<Ref<boolean>>('isMouseHovered', ref(false))
</script>

<template>
  <v-list-item
    v-bind="linkProps"
    :active="isActive"
    class="vertical-menu-link"
    :class="{ 'list-link-active': isActive }"
  >
    <!-- prepend icon -->
    <template #prepend>
      <v-icon>
        <component :is="item.icon || appConfig.menuDefaultIcon" size="18" />
      </v-icon>
    </template>

    <!-- name -->
    <template #title>
      <v-fade-transition>
        <v-list-item-title v-show="!isVerticalMenuMini || isMouseHovered">
          {{ item.name }}
        </v-list-item-title>
      </v-fade-transition>
    </template>

    <!-- badge -->
    <template #append>
      <v-list-item-action
        v-show="item.badgeContent && (!isVerticalMenuMini || isMouseHovered)"
      >
        <v-chip :class="`bg-${item.badgeColor}`" size="x-small">
          {{ item.badgeContent }}
        </v-chip>
      </v-list-item-action>
    </template>
  </v-list-item>
</template>
