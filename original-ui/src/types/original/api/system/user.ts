import type { EnquiryPageDto } from '@/types/original/api/core'
import type { ReplaceField } from '@/types/original/generic'

export interface EnquiryUserPageDto extends EnquiryPageDto {
  username: string | null
  roleIds: string[]
}

export interface UserPageVo {
  id: string
  username: string
  gender?: string
  email?: string
  phoneNumber?: string
  avatar?: string
  roles: string[]
  createdTime: string
}

export interface CreateUserDto {
  username: string
  gender: string | null
  birthday: string | null
  email: string | null
  phoneNumber: string | null
  password: string
  roleIds: string[]
}

export type UpdateUserDto = UserDetailsVo

export interface ValidateUsernameUniqueDto {
  id?: string
  username: string
}

export interface ValidateEmailUniqueDto {
  id?: string
  email: string
}

export interface ValidatePhoneNumberUniqueDto {
  id?: string
  phoneNumber: string
}

export interface UserDetailsVo {
  id: string
  username: string
  gender: string | null
  birthday: string | null
  email: string | null
  phoneNumber: string | null
  roleIds: string[]
}

export type UserForm = ReplaceField<
  CreateUserDto & UpdateUserDto,
  'birthday',
  Date | null
>
