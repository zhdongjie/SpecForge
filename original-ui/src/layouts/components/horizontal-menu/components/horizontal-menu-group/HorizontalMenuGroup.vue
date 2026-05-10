<script lang="ts" setup>
import type { GroupMenu } from '@/types/original/menu'
import { IconChevronRight } from '@tabler/icons-vue'
import appConfig from '@/appConfig'

import HorizontalMenuLink from '@/layouts/components/horizontal-menu/components/horizontal-menu-link/HorizontalMenuLink.vue'
import useHorizontalMenu from '@/layouts/composables/horizontal-menu/useHorizontalMenu'

import useHorizontalMenuGroup from '@/layouts/composables/horizontal-menu/useHorizontalMenuGroup'

defineOptions({
  name: 'HorizontalMenuGroup',
  components: {
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

// watch
// Solution: When the menu's opening method is not hover, switching components cannot close all parent menus
watch(isOpen, (value: boolean) => {
  // make the current menu's open state consistent with the parent level
  parentIsOpen.value = value
})

// parent level menu's open state
const parentIsOpen = inject<Ref<boolean>>('isParentMenuOpen', ref(false))

// current menu's open state
provide('isParentMenuOpen', isOpen)
</script>

<template>
  <v-menu
    v-model="isOpen"
    class="horizontal-menu-group"
    :close-on-content-click="!isOpen"
    location="end"
    :lose-delay="0"
    :open-delay="0"
    :open-on-hover="horizontalMenuGroupOpenOnHover"
    transition="slide-y-reverse-transition"
    width="220"
  >
    <template #activator="{ props }">
      <v-list-item
        v-bind="props"
        :class="{
          'horizontal-menu-group-open': isOpen,
          'horizontal-menu-group-active': isActive
        }"
        density="comfortable"
        :link="true"
        :variant="isActive ? 'tonal' : 'text'"
      >
        <!-- prepend icon -->
        <template #prepend>
          <v-icon>
            <component :is="item.icon || appConfig.menuDefaultIcon" size="18" />
          </v-icon>
        </template>

        <template #title>
          <div class="d-flex align-center justify-space-between">
            <!-- name -->
            <v-list-item-title>
              {{ item.name }}
            </v-list-item-title>

            <!-- menu group badge -->
            <v-list-item-action v-show="item.badgeContent">
              <v-chip :class="`bg-${item.badgeColor}`" size="x-small">
                {{ item.badgeContent }}
              </v-chip>
            </v-list-item-action>
          </div>
        </template>

        <!-- append icon -->
        <template #append>
          <v-icon>
            <icon-chevron-right :size="16"></icon-chevron-right>
          </v-icon>
        </template>
      </v-list-item>
    </template>

    <!-- menu group items -->
    <v-list density="comfortable" :lines="false" :nav="true">
      <component
        :is="resolveMenuComponent(child)"
        v-for="child in item.children"
        :key="child.id"
        :item="child"
      ></component>
    </v-list>
  </v-menu>
</template>
