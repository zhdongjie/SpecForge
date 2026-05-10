import type { GroupMenu } from '@/types/original/menu'
import useMenu from '@/layouts/composables/useMenu'

const useHorizontalMenuGroup = (item: GroupMenu) => {
  const { isGroupActive } = useMenu()
  const { currentRoute } = useRouter()

  // ------------------------------------------------
  // isOpen
  // ------------------------------------------------
  const isOpen = ref(false)

  // ------------------------------------------------
  // isActive
  // ------------------------------------------------
  const isActive = ref(false)

  const updateIsActive = () => {
    if (item.children.length > 0) {
      isActive.value = isGroupActive(item.children)
    }
  }

  // ------------------------------------------------
  // currentRoute
  // ------------------------------------------------
  watch(currentRoute, updateIsActive, { immediate: true })

  return {
    isOpen,
    isActive
  }
}
export default useHorizontalMenuGroup
