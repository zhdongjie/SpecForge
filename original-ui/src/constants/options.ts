import type {
  CardWithOption,
  ContentLayoutOption,
  ContentWidthOption,
  LanguageOption,
  MenuGroupOpenOnOption,
  PageSizeOption,
  RouterTransitionOption,
  SidebarTypeOption,
  ThemeOption
} from '@/types/original/options'
import {
  IconCircle,
  IconHandClick,
  IconHandFinger,
  IconInnerShadowBottom,
  IconLayoutDistributeHorizontal,
  IconLayoutDistributeVertical,
  IconLayoutNavbar,
  IconLayoutSidebar,
  IconLayoutSidebarLeftCollapse
} from '@tabler/icons-vue'

export const languagesOptions: LanguageOption[] = [
  { label: '$original.app.customizer.chinese', value: 'zh-CN' },
  { label: '$original.app.customizer.english', value: 'en-US' }
]

export const contentLayoutOptions: ContentLayoutOption[] = [
  { value: 'vertical', icon: IconLayoutSidebar },
  { value: 'horizontal', icon: IconLayoutNavbar }
]

export const themeOptions: ThemeOption[] = [
  {
    title: '$original.app.customizer.themeLightColor',
    items: [
      { value: 'light-orange', color: '#fb9678' },
      { value: 'light-blue', color: '#1a9bfc' },
      { value: 'light-red', color: '#ff5c8e' },
      { value: 'light-purple', color: '#7352ff' },
      { value: 'light-green', color: '#00cec3' },
      { value: 'light-indigo', color: '#1e4db7' }
    ]
  },
  {
    title: '$original.app.customizer.themeDarkColor',
    items: [
      { value: 'dark-orange', color: '#fb9678' },
      { value: 'dark-blue', color: '#1a9bfc' },
      { value: 'dark-red', color: '#ff5c8e' },
      { value: 'dark-purple', color: '#7352ff' },
      { value: 'dark-green', color: '#00cec3' },
      { value: 'dark-indigo', color: '#1e4db7' }
    ]
  }
]

export const contentWidthOptions: ContentWidthOption[] = [
  { value: 'boxed', icon: IconLayoutDistributeVertical },
  { value: 'full', icon: IconLayoutDistributeHorizontal }
]

export const sidebarTypeOptions: SidebarTypeOption[] = [
  { value: false, icon: IconLayoutSidebar },
  {
    value: true,
    icon: IconLayoutSidebarLeftCollapse
  }
]

export const cardWithOptions: CardWithOption[] = [
  { value: 'shadow', icon: IconInnerShadowBottom },
  { value: 'border', icon: IconCircle }
]

export const menuGroupOpenOnOptions: MenuGroupOpenOnOption[] = [
  { value: true, icon: IconHandFinger },
  { value: false, icon: IconHandClick }
]

export const routerTransitionOptions: RouterTransitionOption[] = [
  'scroll-x-transition',
  'fade-transition'
]

export const pageSizeOptions: PageSizeOption[] = [
  { title: '10', value: 10 },
  { title: '20', value: 20 },
  { title: '50', value: 50 },
  { title: '100', value: 100 },
  { title: '200', value: 200 },
  { title: '500', value: 500 }
]
