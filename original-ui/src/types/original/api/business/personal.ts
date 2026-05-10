import type { BadgeColor } from '@/types/original/menu'

export interface MeVo {
  username: string
  gender?: string
  birthday?: string
  email?: string
  phoneNumber?: string
  avatar?: string
  roles: string[]
  routers: RouterVo[]
  buttons: string[]
  createdTime: string
}

export interface ChangePasswordDto {
  oldPassword: string
  newPassword: string
  confirmPassword: string
}

export interface BaseRouter {
  id: string
  parentId: string
  name: string
  resource: string
  sort: number
  visible: boolean
  icon?: string
  badgeContent?: string
  badgeColor?: BadgeColor
}

export interface Subheader extends BaseRouter {
  type: 'SUBHEADER'
}

export interface Group extends BaseRouter {
  type: 'GROUP'
}

export interface Template extends BaseRouter {
  type: 'TEMPLATE'
  routerPath: string
  componentPath: string
  keepAlive: boolean
}

export interface Link extends BaseRouter {
  type: 'LINK'
  href: string
  target: '_blank' | '_self'
}

export type RouterVo = Subheader | Group | Template | Link
