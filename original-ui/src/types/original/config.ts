export type Language = 'zh-CN' | 'en-US'
export type Layout = 'blank' | 'content'
export type ContentWidth = 'full' | 'boxed'
export type CardWith = 'shadow' | 'border'
export type ContentLayout = 'vertical' | 'horizontal'
export type RouterTransition = 'scroll-x-transition' | 'fade-transition'
export type Theme =
  | 'dark-orange'
  | 'dark-blue'
  | 'dark-red'
  | 'dark-purple'
  | 'dark-green'
  | 'dark-indigo'
  | 'light-orange'
  | 'light-blue'
  | 'light-red'
  | 'light-purple'
  | 'light-green'
  | 'light-indigo'

export interface AppConfig {
  name: string
  logo: string
  avatar: string
  menuDefaultIcon: string
  language: Language
  theme: Theme
  contentLayout: ContentLayout
  contentWidth: ContentWidth
  cardWith: CardWith
  isVerticalMenuMini: boolean
  isVerticalMenuAccordion: boolean
  horizontalMenuGroupOpenOnHover: boolean
  routerTransition: RouterTransition
}
