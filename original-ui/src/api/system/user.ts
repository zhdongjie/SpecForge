import type { PaginateVo } from '@/types/original/api/core'
import type {
  CreateUserDto,
  EnquiryUserPageDto,
  UpdateUserDto,
  UserDetailsVo,
  UserPageVo,
  ValidateUsernameUniqueDto,
  ValidateEmailUniqueDto,
  ValidatePhoneNumberUniqueDto
} from '@/types/original/api/system/user'
import request from '@/plugins/axios'

const enquiryUserPageApi = (searchInfo: EnquiryUserPageDto) => {
  return request.get<EnquiryUserPageDto, PaginateVo<UserPageVo>>(
    '/v1/system/user/page',
    searchInfo
  )
}

const validateUserUsernameUniqueApi = (
  validateUsernameUniqueDto: ValidateUsernameUniqueDto
) => {
  return request.get<ValidateUsernameUniqueDto, boolean>(
    '/v1/system/user/username/unique',
    validateUsernameUniqueDto
  )
}

const validateUserEmailUniqueApi = (
  validateEmailUniqueDto: ValidateEmailUniqueDto
) => {
  return request.get<ValidateEmailUniqueDto, boolean>(
    '/v1/system/user/email/unique',
    validateEmailUniqueDto
  )
}

const validateUserPhoneNumberUniqueApi = (
  validatePhoneNumberUniqueDto: ValidatePhoneNumberUniqueDto
) => {
  return request.get<ValidatePhoneNumberUniqueDto, boolean>(
    '/v1/system/user/phone-number/unique',
    validatePhoneNumberUniqueDto
  )
}

const createUserApi = (createUserDto: CreateUserDto) => {
  return request.post<CreateUserDto, null>('/v1/system/user', createUserDto)
}

const deleteUserApi = (userIds: string[]) => {
  return request.delete<{ userIds: string[] }, null>('/v1/system/user', {
    userIds
  })
}

const enquiryUserDetailsApi = (userId: string) => {
  return request.get<null, UserDetailsVo>(`/v1/system/user/${userId}`)
}

const editUserApi = (updateUserDto: UpdateUserDto) => {
  return request.put<UpdateUserDto, null>('/v1/system/user', updateUserDto)
}

export {
  createUserApi,
  deleteUserApi,
  editUserApi,
  enquiryUserDetailsApi,
  enquiryUserPageApi,
  validateUserUsernameUniqueApi,
  validateUserEmailUniqueApi,
  validateUserPhoneNumberUniqueApi
}
