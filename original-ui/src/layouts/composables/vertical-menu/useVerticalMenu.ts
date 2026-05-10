import type { VerticalMenu } from '@/types/original/menu'

const useVerticalMenu = () => {
  const isMouseHovered = ref(false)

  const resolveItemComponent = (item: VerticalMenu) => {
    const type = item.type
    if (type === 'SUBHEADER') return 'vertical-menu-subheader'
    return type === 'GROUP' ? 'vertical-menu-group' : 'vertical-menu-link'
  }

  return {
    isMouseHovered,
    resolveItemComponent
  }
}

export default useVerticalMenu
