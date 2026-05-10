import type { RouteLocationRaw } from 'vue-router'
import type { TreeNode } from '@/types/original/generic'

export type BadgeColor =
  | 'primary'
  | 'secondary'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'

export interface BaseMenu {
  name: string
  icon?: string
  badgeContent?: string
  badgeColor?: BadgeColor
  sort: number
}

export interface SubheaderMenu extends BaseMenu, TreeNode<SubMenu> {
  type: 'SUBHEADER'
}

export interface GroupMenu extends BaseMenu, TreeNode<SubMenu> {
  type: 'GROUP'
}

export interface TemplateMenu extends BaseMenu, TreeNode<SubMenu> {
  type: 'TEMPLATE'
  to: RouteLocationRaw
}

export interface LinkMenu extends BaseMenu, TreeNode<SubMenu> {
  type: 'LINK'
  to: LinkProps
}

export type SubMenu = GroupMenu | TemplateMenu | LinkMenu

export type HorizontalMenu = SubheaderMenu | GroupMenu | TemplateMenu | LinkMenu

export type VerticalMenu =
  | Omit<SubheaderMenu, 'icon' | 'badgeContent' | 'badgeColor'>
  | GroupMenu
  | TemplateMenu
  | LinkMenu

export type Menu = HorizontalMenu | VerticalMenu

export interface LinkProps {
  href: string
  target?: string
  rel?: string
}
