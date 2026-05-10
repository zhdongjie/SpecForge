import type {
  LoginDto,
  RefreshTokenDto,
  RegisterDto,
  TokenVo
} from '@/types/original/api/authorize'
import type { ValidateUsernameUniqueDto } from '@/types/original/api/system/user'
import request from '@/plugins/axios'

const validateAuthorizeUsernameUniqueApi = (
  validateUsernameUniqueDto: ValidateUsernameUniqueDto
) => {
  return request.get<ValidateUsernameUniqueDto, boolean>(
    '/v1/authorize/username/unique',
    validateUsernameUniqueDto
  )
}

const registerApi = (registerInfo: RegisterDto) => {
  return request.post<RegisterDto, null>('/v1/authorize/register', registerInfo)
}

const loginApi = (userInfo: LoginDto) => {
  return request.post<LoginDto, TokenVo>('/v1/authorize/login', userInfo)
}

const refreshTokenApi = (tokenInfo: RefreshTokenDto) => {
  return request.put<RefreshTokenDto, TokenVo>(
    '/v1/authorize/refresh-token',
    tokenInfo
  )
}

export {
  loginApi,
  refreshTokenApi,
  registerApi,
  validateAuthorizeUsernameUniqueApi
}
