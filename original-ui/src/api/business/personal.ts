import type {
  ChangePasswordDto,
  MeVo
} from '@/types/original/api/business/personal'
import request from '@/plugins/axios'

const meApi = () => {
  return request.get<null, MeVo>('/v1/business/personal/me')
}

const changePasswordApi = (changePasswordDto: ChangePasswordDto) => {
  return request.patch<ChangePasswordDto, null>(
    '/v1/business/personal/password',
    changePasswordDto
  )
}

export { changePasswordApi, meApi }
