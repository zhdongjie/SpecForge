export interface RegisterDto {
  username: string
  password: string
  confirmPassword: string
}

export type RegisterForm = RegisterDto

export interface LoginDto {
  username: string
  password: string
  rememberMe: boolean
}

export type LoginForm = LoginDto

export interface TokenVo {
  accessToken: string
  refreshToken: string
}

export type RefreshTokenDto = TokenVo
