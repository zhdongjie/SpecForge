import type { AppConfig } from '@/types/original/config'

export default <AppConfig>{
  name: 'Original',
  logo: new URL('@/assets/images/logo.png', import.meta.url).href,
  avatar: new URL('@/assets/images/avatar.jpg', import.meta.url).href,
  menuDefaultIcon: 'icon-circle-dot',
  language: 'zh-CN',
  theme: 'dark-orange',
  contentLayout: 'vertical',
  contentWidth: 'boxed',
  cardWith: 'shadow',
  isVerticalMenuMini: false,
  isVerticalMenuAccordion: true,
  horizontalMenuGroupOpenOnHover: true,
  routerTransition: 'scroll-x-transition'
}
