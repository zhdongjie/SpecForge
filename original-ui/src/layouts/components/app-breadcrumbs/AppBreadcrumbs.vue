<script setup lang="ts">
import type { Menu, SubMenu, TemplateMenu } from '@/types/original/menu'
import { IconHome } from '@tabler/icons-vue'
import { useDisplay } from 'vuetify'
import useMenu from '@/layouts/composables/useMenu'
import { findTreeNode, findTreePath } from '@/utils/tree'
import { BreadcrumbItem } from '@/types/original/generic'

defineOptions({
  name: 'AppBreadcrumbs'
})

// props
defineProps({
  showIcon: {
    type: Boolean as PropType<boolean>,
    default: true
  }
})

// composables
const { resolveMenuLinkProps } = useMenu()
const route = useRoute()
const userStore = useUserStore()
const { mobile } = useDisplay()
const { t } = useI18n()

const menuItems = userStore.getMenus

// computed
const items = computed<BreadcrumbItem[]>(() => {
  const name = route.meta.title

  if (!name) return []

  const currentRouter = findTreePath<Menu>('name', name, menuItems)
  const firstTemplate = findTreeNode<Menu>('type', 'TEMPLATE', menuItems)

  // Filter menus and construct breadcrumbs
  const breadcrumbs = currentRouter
    // filter menus
    .filter((item) => item.type === 'GROUP' || item.type === 'TEMPLATE')
    // construct breadcrumb
    .map((item, index, array) => {
      const isLast = index === array.length - 1
      const templateItem =
        item.type === 'TEMPLATE'
          ? item
          : findTreeNode<SubMenu>('type', 'TEMPLATE', item.children)

      const breadcrumb: BreadcrumbItem = {
        title: item.name,
        disabled: isLast
      }

      if (isTemplateMenu(templateItem)) {
        return {
          ...breadcrumb,
          ...resolveMenuLinkProps(templateItem)
        }
      }

      return breadcrumb
    })

  // breadcrumbs
  return breadcrumbs.length === 0
    ? []
    : [
        ...(isTemplateMenu(firstTemplate)
          ? [
              {
                title: t('$original.common.home'),
                ...resolveMenuLinkProps(firstTemplate),
                disabled: breadcrumbs.length === 0
              }
            ]
          : []),
        ...breadcrumbs
      ]
})

// methods
const isTemplateMenu = (menu: Menu | null): menu is TemplateMenu => {
  return menu !== null && menu.type === 'TEMPLATE'
}
</script>

<template>
  <v-breadcrumbs
    v-show="!mobile"
    class="text-body-2"
    density="compact"
    :items="items"
  >
    <template v-if="showIcon" #prepend>
      <icon-home :size="18" :style="{ marginBottom: '1px' }" />
    </template>
  </v-breadcrumbs>
</template>
