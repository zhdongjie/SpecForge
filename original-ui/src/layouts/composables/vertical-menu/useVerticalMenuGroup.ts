import type { GroupMenu } from '@/types/original/menu'
import useMenu from '@/layouts/composables/useMenu'

const useVerticalMenuGroup = (item: GroupMenu) => {
  const addStore = useAppStore()
  // ------------------------------------------------
  // isMouseHovered
  // ------------------------------------------------
  const isMouseHovered = inject<Ref<boolean>>('isMouseHovered', ref(false))
  watch(isMouseHovered, (value) => {
    if (isVerticalMenuMini.value) {
      isOpen.value = value ? isActive.value : false
      toggleGroup(isOpen.value)
    }
  })

  // ------------------------------------------------
  // isVerticalMenuMini
  // ------------------------------------------------
  const { isVerticalMenuMini } = storeToRefs(addStore)
  watch(isVerticalMenuMini, (value) => {
    isOpen.value = value ? false : isActive.value
    toggleGroup(isOpen.value)
  })

  // ------------------------------------------------
  // openGroups
  // ------------------------------------------------
  const openGroups = inject<Ref<string[]>>('openGroups', ref([]))
  watch(
    openGroups,
    (currentOpenGroups) => {
      const clickedGroup = currentOpenGroups.at(-1)
      if (
        clickedGroup !== item.id &&
        !isActive.value &&
        !doesHaveChild(clickedGroup)
      ) {
        isOpen.value = false
      }
    },
    { deep: true }
  )

  // ------------------------------------------------
  // isOpen
  // ------------------------------------------------
  const isOpen = ref(false)
  const { isVerticalMenuAccordion: isAccordion } = storeToRefs(addStore)
  watch(isOpen, (value) => {
    if (isAccordion.value) {
      toggleGroup(value)
    }
  })

  const updateGroupOpen = (value: boolean) => {
    isOpen.value = value
  }

  // ------------------------------------------------
  // isActive
  // ------------------------------------------------
  const isActive = ref(false)
  watch(isActive, (value) => {
    isOpen.value = value && !isVerticalMenuMini.value
  })

  const { isGroupActive } = useMenu()
  const updateIsActive = () => {
    if (item.children.length > 0) {
      isActive.value = isGroupActive(item.children)
    }
  }

  // ------------------------------------------------
  // currentRoute
  // ------------------------------------------------
  const { currentRoute } = useRouter()
  watch(currentRoute, updateIsActive, { immediate: true })

  // ------------------------------------------------
  // Other Methods
  // ------------------------------------------------
  const doesHaveChild = (id?: string) => {
    return item.children.some((child) => child.id === id)
  }

  const toggleGroup = (open: boolean) => {
    const index = openGroups.value.indexOf(item.id)
    if (open && index === -1) {
      openGroups.value.push(item.id)
    } else if (!open && index !== -1) {
      openGroups.value.splice(index, 1)
    }
  }

  return {
    isOpen,
    isActive,
    openGroups,
    isMouseHovered,
    updateGroupOpen,
    updateIsActive
  }
}

export default useVerticalMenuGroup
