<script lang="ts" setup>
import type { LinkMenu, TemplateMenu } from '@/types/original/menu'
import appConfig from '@/appConfig'
import useMenuLink from '@/layouts/composables/useMenuLink'

defineOptions({
  name: 'HorizontalMenuHeaderLink'
})

// props
const componentProps = defineProps({
  item: {
    type: Object as PropType<TemplateMenu | LinkMenu>,
    required: true
  }
})

const propsRefs = toRefs(componentProps)

// composables
const { isActive, linkProps } = useMenuLink(propsRefs.item.value)
</script>

<template>
  <v-btn
    v-bind="linkProps"
    class="horizontal-menu-header horizontal-menu-header-link"
    :class="{ 'horizontal-menu-header-link-active': isActive }"
    :variant="isActive ? 'tonal' : 'text'"
  >
    <!-- icon -->
    <v-icon :start="true">
      <component :is="item.icon || appConfig.menuDefaultIcon" size="20" />
    </v-icon>

    <div class="d-flex align-center justify-space-between">
      <!-- name -->
      <span>{{ item.name }}</span>

      <!-- menu group badge -->
      <v-list-item-action v-show="item.badgeContent" class="ml-2">
        <v-chip :class="`bg-${item.badgeColor}`" size="x-small">
          {{ item.badgeContent }}
        </v-chip>
      </v-list-item-action>
    </div>
  </v-btn>
</template>
