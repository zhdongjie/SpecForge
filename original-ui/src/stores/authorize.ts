import type { LoginDto } from '@/types/original/api/authorize'
import type { Token } from '@/types/original/store'
import { loginApi } from '@/api'
import router from '@/plugins/router'
import { resetDynamicRoutes } from '@/routes/dynamicRoutes'

const STORE_KEY = 'original-authorize'

/**
 * authorize store for managing authentication state
 */
export const useAuthorizeStore = defineStore(STORE_KEY, {
  state: (): Token => ({
    accessToken: '',
    refreshToken: ''
  }),

  getters: {
    /**
     * check if user is logged in
     */
    isLoggedIn: (state) => !!state.accessToken
  },

  actions: {
    /**
     * setup token information
     */
    setupToken(tokenInfo: Token) {
      this.accessToken = tokenInfo.accessToken
      this.refreshToken = tokenInfo.refreshToken
    },

    /**
     * login with username and password
     */
    login(loginDto: LoginDto) {
      return new Promise((resolve, reject) => {
        loginApi(loginDto)
          .then((response) => {
            const { data: tokenInfo } = response
            this.setupToken(tokenInfo)

            resolve(response)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    /**
     * logout and clear user data
     */
    async logout(shouldRedirectToLogin = true) {
      const userStore = useUserStore()
      const { language } = useAppStore()

      // clear user information
      userStore.$reset()

      // clear token
      this.$reset()

      if (shouldRedirectToLogin) {
        await router.replace({
          name: 'authorize-login',
          params: { locale: language }
        })
      }

      // reset dynamic routes
      resetDynamicRoutes()
    }
  },

  persist: {
    key: STORE_KEY,
    storage: localStorage
  }
})
