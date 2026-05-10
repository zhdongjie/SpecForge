<script lang="ts" setup>
import type { LinkMenu, TemplateMenu } from '@/types/original/menu'
import appConfig from '@/appConfig'
import useMenuLink from '@/layouts/composables/useMenuLink'

defineOptions({
  name: 'HorizontalMenuLink'
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
const { linkProps, isActive } = useMenuLink(propsRefs.item.value)

const isParentMenuOpen = inject<Ref<boolean>>('isParentMenuOpen', ref(false))
</script>

<template>
  <v-list-item
    v-bind="linkProps"
    :active="isActive"
    density="comfortable"
    @click="isParentMenuOpen = false"
  >
    <!-- icon -->
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
  </v-list-item>
</template>
