import { useDisplay } from 'vuetify'

const useLayout = () => {
  const breakpointLayoutToggle = () => {
    const { lgAndUp } = useDisplay()
    const { contentLayout } = storeToRefs(useAppStore())

    // ? This is flag which hold nav type need to render when going to lgAndUp from mdAndDown
    /*
    ? Requirement: When we set  to `horizontal` nav and hit the `mdAndDown` breakpoint nav type is changed to `vertical`.
    ? Now if we go back to `lgAndUp` breakpoint from `mdAndDown` how we will know which we previous nav type in large device user viewed?
    */
    //  Let's assign value we get from themeConfig as default value of lgAndUpNav
    const lgAndUpNav = ref(contentLayout)

    // There might be case where use manually switch from vertical to horizontal nav and vice versa in `lgAndUp` screen
    // So when user comes back from `mdAndDown` to `lgAndUp` we can set updated nav type
    // For this we need to update the `lgAndUpNav` value if screen is `lgAndUp`
    watch(contentLayout, (value) => {
      if (lgAndUp.value) lgAndUpNav.value = value
    })

    // This is layout switching part
    // If it's `mdAndDown` => We will use vertical nav no matter what previous nav type was
    // Or if it's `lgAndUp` we need to switch back to `lgAndUp` nav type. For this we will track property `lgAndUpNav`
    watch(
      () => lgAndUp.value,
      (value) => {
        contentLayout.value = value ? lgAndUpNav.value : 'vertical'
      },
      {
        immediate: true
      }
    )
  }

  return {
    breakpointLayoutToggle
  }
}
export default useLayout
