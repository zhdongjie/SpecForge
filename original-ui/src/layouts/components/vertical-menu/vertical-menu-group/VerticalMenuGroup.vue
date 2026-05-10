<script lang="ts" setup>
import type { GroupMenu } from '@/types/original/menu'
import appConfig from '@/appConfig'

import VerticalMenuLink from '@/layouts/components/vertical-menu/vertical-menu-link/VerticalMenuLink.vue'
import useVerticalMenu from '@/layouts/composables/vertical-menu/useVerticalMenu'
import useVerticalMenuGroup from '@/layouts/composables/vertical-menu/useVerticalMenuGroup'

defineOptions({
  name: 'VerticalMenuGroup',
  components: {
    VerticalMenuLink
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
const { isVerticalMenuMini } = storeToRefs(useAppStore())
const { resolveItemComponent } = useVerticalMenu()
const { isOpen, isActive, updateGroupOpen } = useVerticalMenuGroup(
  propsRefs.item.value
)

const isMouseHovered = inject<Ref<boolean>>('isMouseHovered', ref(false))
</script>

<template>
  <v-list-group class="vertical-menu-group" :value="item.id">
    <!-- menu group -->
    <template #activator="{ props }">
      <v-list-item
        v-bind="props"
        :class="{ 'list-group-active': isActive }"
        @click="updateGroupOpen(!isOpen)"
      >
        <!-- menu group icon -->
        <template #prepend>
          <v-icon>
            <component :is="item.icon || appConfig.menuDefaultIcon" size="18" />
          </v-icon>
        </template>

        <template #title>
          <div class="d-flex align-center justify-space-between">
            <!-- menu group title -->
            <v-fade-transition>
              <v-list-item-title v-show="!isVerticalMenuMini || isMouseHovered">
                {{ item.name }}
              </v-list-item-title>
            </v-fade-transition>
            <!-- menu group badge -->
            <v-list-item-action
              v-show="
                item.badgeContent && (!isVerticalMenuMini || isMouseHovered)
              "
            >
              <v-chip :class="`bg-${item.badgeColor}`" size="x-small">
                {{ item.badgeContent }}
              </v-chip>
            </v-list-item-action>
          </div>
        </template>
      </v-list-item>
    </template>

    <!-- menu group items -->
    <component
      :is="resolveItemComponent(child)"
      v-for="child in item.children"
      :key="child.id"
      :item="child"
    ></component>
  </v-list-group>
</template>
