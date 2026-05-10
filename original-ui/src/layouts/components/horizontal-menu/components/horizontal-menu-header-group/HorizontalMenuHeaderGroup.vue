<script lang="ts" setup>
import type { GroupMenu } from '@/types/original/menu'
import { IconChevronDown } from '@tabler/icons-vue'
import appConfig from '@/appConfig'

import HorizontalMenuGroup from '@/layouts/components/horizontal-menu/components/horizontal-menu-group/HorizontalMenuGroup.vue'
import HorizontalMenuLink from '@/layouts/components/horizontal-menu/components/horizontal-menu-link/HorizontalMenuLink.vue'

import useHorizontalMenu from '@/layouts/composables/horizontal-menu/useHorizontalMenu'
import useHorizontalMenuGroup from '@/layouts/composables/horizontal-menu/useHorizontalMenuGroup'

defineOptions({
  name: 'HorizontalMenuHeaderGroup',
  components: {
    HorizontalMenuGroup,
    HorizontalMenuLink
  }
})

// props
const componentProps = defineProps({
  item: {
    type: Object as PropType<GroupMenu>,
    required: true
  }
})

const propsRefs = toRefs(componentProps)

// composables
const { horizontalMenuGroupOpenOnHover } = storeToRefs(useAppStore())
const { resolveMenuComponent } = useHorizontalMenu()
const { isActive, isOpen } = useHorizontalMenuGroup(propsRefs.item.value)

provide('isParentMenuOpen', isOpen)
</script>

<template>
  <v-menu
    v-model="isOpen"
    class="horizontal-menu-header-group"
    :close-on-content-click="!isOpen"
    :lose-delay="0"
    :open-delay="0"
    :open-on-hover="horizontalMenuGroupOpenOnHover"
    transition="slide-y-reverse-transition"
    width="220"
  >
    <template #activator="{ props }">
      <!-- header group -->
      <v-btn
        v-bind="props"
        class="horizontal-menu-header"
        :class="{
          'horizontal-menu-header-group-open': isOpen,
          'horizontal-menu-header-group-active': isActive
        }"
        :variant="isActive ? 'tonal' : 'text'"
      >
        <!-- prepend icon -->
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

        <!-- append icon -->
        <v-icon :end="true">
          <icon-chevron-down :size="16"></icon-chevron-down>
        </v-icon>
      </v-btn>
    </template>

    <!-- menu group items -->
    <v-list :lines="false" :nav="true">
      <component
        :is="resolveMenuComponent(child)"
        v-for="child in item.children"
        :key="child.id"
        :item="child"
      ></component>
    </v-list>
  </v-menu>
</template>
