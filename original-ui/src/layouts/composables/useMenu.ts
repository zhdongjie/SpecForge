import type { LinkMenu, SubMenu, TemplateMenu } from '@/types/original/menu'
import type { RouteRecordName } from 'vue-router'

const useMenu = () => {
  const router = useRouter()
  const { currentRoute } = useRouter()

  const menuLinkProps = computed(() => (item: TemplateMenu | LinkMenu) => {
    return resolveMenuLinkProps(item)
  })

  const resolveMenuLinkProps = (item: TemplateMenu | LinkMenu) => {
    if (item.type === 'TEMPLATE') {
      return {
        to: typeof item.to === 'string' ? { name: item.to } : item.to
      }
    }

    if (item.type === 'LINK') {
      return {
        target: '_blank',
        rel: 'nofollow',
        ...item.to
      }
    }
  }

  const resolveLinkRouteName = (
    link: TemplateMenu | LinkMenu
  ): RouteRecordName | null => {
    if (link.type === 'TEMPLATE') {
      if (typeof link.to === 'string') {
        return link.to
      }
      const { name } = router.resolve(link.to)
      return name
    }
    return null
  }

  const isLinkActive = (link: TemplateMenu | LinkMenu) => {
    // Matched routes array of current route
    const matchedRoutes = currentRoute.value.matched

    // Check if provided route matches route's matched route
    const resolveRoutedName = resolveLinkRouteName(link)

    if (!resolveRoutedName) return false

    return matchedRoutes.some((route) => {
      return route.name === resolveRoutedName
    })
  }

  const isGroupActive = (children: SubMenu[]): boolean => {
    return children.some((child) => {
      return child.type === 'GROUP'
        ? isGroupActive(child.children)
        : isLinkActive(child)
    })
  }

  return {
    menuLinkProps,
    isLinkActive,
    isGroupActive,
    resolveMenuLinkProps
  }
}
export default useMenu
