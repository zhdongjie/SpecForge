<script lang="ts" setup>
import type { LoginDto, LoginForm } from '@/types/original/api/authorize'
import { IconEye, IconEyeOff } from '@tabler/icons-vue'
import { toTypedSchema } from '@vee-validate/yup'
import { useField, useForm } from 'vee-validate'
import { useDisplay } from 'vuetify'
import * as yup from 'yup'
import appConfig from '@/appConfig'
import AuthorizeHeader from '@/pages/authorize/components/AuthorizeHeader.vue'

import { setBackendErrors } from '@/utils/errorApply'

defineOptions({
  name: 'AuthorizeLogin'
})

// states
const isPasswordVisible = ref(false)
const loginButtonLoading = ref(false)

// composables
const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const authorizeStore = useAuthorizeStore()
const { mobile } = useDisplay()

// error message
const errorMessages = {
  usernameIsRequired: t('$original.authorize.login.usernameIsRequired'),
  passwordIsRequired: t('$original.authorize.login.passwordIsRequired')
}

const schema = yup.object({
  username: yup.string().required(errorMessages.usernameIsRequired),
  password: yup.string().required(errorMessages.passwordIsRequired),
  rememberMe: yup.boolean()
})
const { handleSubmit, meta } = useForm<LoginForm>({
  validationSchema: toTypedSchema(schema),
  name: 'LoginForm',
  initialValues: {
    username: route.query.username ? String(route.query.username) : '',
    password: '',
    rememberMe: false
  }
})

const username = useField<string>('username')
const password = useField<string>('password')
const rememberMe = useField<boolean>('rememberMe')

// methods
const submit = handleSubmit((values, actions) => {
  if (meta.value.valid) {
    // open login button loading
    loginButtonLoading.value = true

    authorizeStore
      .login(values)
      .then(async () => {
        // load user information
        await userStore.me()

        // on success redirect to home
        await router.push('/')
      })
      .catch((error) => {
        setBackendErrors<LoginDto>(error, actions.setFieldError)
      })
      .finally(() => {
        loginButtonLoading.value = false
      })
  }
})
</script>

<template>
  <div class="d-flex align-center justify-center mh-100 authorize-login">
    <v-card class="pa-4 authorize-card" :elevation="mobile ? 0 : 1">
      <!-- authorize header -->
      <authorize-header
        :subtitle="t('$original.authorize.login.subtitle')"
        :title="
          t('$original.authorize.login.title', { appName: appConfig.name })
        "
      />

      <!-- login form -->
      <v-card-text>
        <v-form @submit.prevent="submit">
          <!-- username -->
          <v-text-field
            v-model="username.value.value"
            autocomplete="off"
            base-color="input-border"
            :clearable="true"
            density="comfortable"
            :error-messages="username.errorMessage.value"
            :label="t('$original.authorize.login.username')"
            variant="outlined"
          />

          <!-- password -->
          <v-text-field
            v-model="password.value.value"
            :append-inner-icon="isPasswordVisible ? IconEye : IconEyeOff"
            autocomplete="off"
            base-color="input-border"
            :clearable="true"
            density="comfortable"
            :error-messages="password.errorMessage.value"
            :label="t('$original.authorize.login.password')"
            :type="isPasswordVisible ? 'text' : 'password'"
            variant="outlined"
            @click:append-inner="isPasswordVisible = !isPasswordVisible"
          />

          <div class="d-flex align-center justify-space-between mb-1">
            <!-- remember me -->
            <v-checkbox
              v-model="rememberMe.value.value"
              color="info"
              hide-details
            >
              <template #label>
                <span>
                  {{ t('$original.authorize.login.rememberMe') }}
                </span>
              </template>
            </v-checkbox>

            <!-- forgot password link -->
            <router-link class="text-info" to="/">
              {{ t('$original.authorize.login.forgotPassword') }}
            </router-link>
          </div>

          <!-- submit button -->
          <v-btn
            :block="true"
            color="primary"
            :flat="true"
            height="44"
            :loading="loginButtonLoading"
            type="submit"
            variant="elevated"
          >
            {{ t('$original.authorize.login.login') }}
          </v-btn>

          <!-- register account -->
          <div class="d-flex align-center justify-end mt-4 mb-2">
            <span>{{ t('$original.authorize.login.noAccount') }}</span>
            <router-link
              class="text-info ml-1"
              :to="{ name: 'authorize-register' }"
            >
              {{ t('$original.authorize.login.registerNow') }}
            </router-link>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>
