import type { TokenVo } from '@/types/original/api/authorize'
import type { MeVo, RouterVo } from '@/types/original/api/business/personal'
import type {
  CardWith,
  ContentLayout,
  ContentWidth,
  Language,
  RouterTransition,
  Theme
} from '@/types/original/config'

export interface App {
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

export type User = MeVo
export type Router = RouterVo
export type Token = TokenVo
