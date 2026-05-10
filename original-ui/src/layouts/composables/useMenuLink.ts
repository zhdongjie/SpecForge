import type { LinkMenu, TemplateMenu } from '@/types/original/menu'
import useMenu from '@/layouts/composables/useMenu'

const useMenuLink = (item: TemplateMenu | LinkMenu) => {
  const { isLinkActive, menuLinkProps } = useMenu()
  const { currentRoute } = useRouter()

  // ------------------------------------------------
  // isActive
  // ------------------------------------------------
  const isActive = ref(false)

  // ------------------------------------------------
  // linkProps
  // ------------------------------------------------
  const linkProps = menuLinkProps.value(item)

  // ------------------------------------------------
  // currentRoute
  // ------------------------------------------------
  watch(
    () => currentRoute.value.name,
    () => {
      isActive.value = isLinkActive(item)
    },
    { immediate: true }
  )

  return {
    isActive,
    linkProps
  }
}
export default useMenuLink
