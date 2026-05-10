import type {
  AxiosInstance,
  AxiosRequestConfig,
  InternalAxiosRequestConfig
} from 'axios'
import type { ResponseVo } from '@/types/original/api/core'
import { IconX } from '@tabler/icons-vue'
import axios from 'axios'
import JSONBig from 'json-bigint'
import { stringify } from 'qs'
import { toast } from 'vuetify-sonner'
import { refreshTokenApi } from '@/api'

const request = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: 30_000,
  transformResponse: (data) => {
    try {
      return JSONBig({ storeAsString: true }).parse(data)
    } catch (error) {
      console.error(error || 'json big parse error')
      return data
    }
  }
})

request.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthorizeStore()

    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

let isRefreshing = false
let requests: (() => void)[] = []

request.interceptors.response.use(
  (response) => {
    const { data, config } = response

    if (data.code === 40_100) {
      return isRefreshing
        ? new Promise((resolve) => {
            requests.push(() => {
              resolve(request(config))
            })
          })
        : refreshToken(config)
    }

    if (data.code && data.code !== 20_000) {
      if (data.message) {
        toast.error(data.message, {
          action: {
            buttonProps: {
              icon: IconX,
              size: 'small'
            }
          }
        })
      }
      return Promise.reject(data)
    }

    return data
  },
  (error) => {
    toast.error(error.message, {
      action: {
        buttonProps: {
          icon: IconX,
          size: 'small'
        }
      }
    })
    return Promise.reject(error)
  }
)

const refreshToken = async (config: InternalAxiosRequestConfig) => {
  const authorizeStore = useAuthorizeStore()
  isRefreshing = true

  return refreshTokenApi({
    accessToken: authorizeStore.accessToken,
    refreshToken: authorizeStore.refreshToken
  })
    .then((response) => {
      const { data: tokenInfo } = response
      authorizeStore.setupToken(tokenInfo)
      for (const request of requests) request()
      requests = []
      return request(config)
    })
    .catch((error) => {
      authorizeStore.logout()
      return Promise.reject(error)
    })
    .finally(() => {
      isRefreshing = false
    })
}

class Axios {
  instance: AxiosInstance

  public constructor() {
    this.instance = request
  }

  get<D, T>(
    url: string,
    params?: D,
    config?: AxiosRequestConfig
  ): Promise<ResponseVo<T>> {
    return this.instance({
      method: 'get',
      url,
      params,
      ...config,
      paramsSerializer: (params) => {
        return stringify(params, {
          arrayFormat: 'repeat',
          allowDots: true
        })
      }
    })
  }

  post<D, T>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<ResponseVo<T>> {
    return this.instance({
      method: 'post',
      url,
      data,
      ...config
    })
  }

  put<D, T>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<ResponseVo<T>> {
    return this.instance({
      method: 'put',
      url,
      data,
      ...config
    })
  }

  patch<D, T>(
    url: string,
    data?: D,
    config?: AxiosRequestConfig
  ): Promise<ResponseVo<T>> {
    return this.instance({
      method: 'patch',
      url,
      data,
      ...config
    })
  }

  delete<D, T>(
    url: string,
    params?: D,
    config?: AxiosRequestConfig
  ): Promise<ResponseVo<T>> {
    return this.instance({
      method: 'delete',
      url,
      params,
      ...config,
      paramsSerializer: (params) => {
        return stringify(params, {
          arrayFormat: 'repeat',
          allowDots: true
        })
      }
    })
  }
}

export default new Axios()
