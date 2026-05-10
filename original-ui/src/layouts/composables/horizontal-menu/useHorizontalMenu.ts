import type { HorizontalMenu, SubMenu } from '@/types/original/menu'

const useHorizontalMenu = () => {
  const resolveHeaderComponent = (item: HorizontalMenu) => {
    const type = item.type
    return type === 'SUBHEADER' || type === 'GROUP'
      ? 'horizontal-menu-header-group'
      : 'horizontal-menu-header-link'
  }

  const resolveMenuComponent = (item: SubMenu) => {
    const type = item.type
    return type === 'GROUP' ? 'horizontal-menu-group' : 'horizontal-menu-link'
  }

  return {
    resolveHeaderComponent,
    resolveMenuComponent
  }
}
export default useHorizontalMenu
