<script lang="ts" setup>
import type { RegisterDto, RegisterForm } from '@/types/original/api/authorize'
import { IconEye, IconEyeOff } from '@tabler/icons-vue'
import { toTypedSchema } from '@vee-validate/yup'
import { useField, useForm } from 'vee-validate'
import { useDisplay } from 'vuetify'
import * as yup from 'yup'
import { registerApi, validateAuthorizeUsernameUniqueApi } from '@/api'
import regex from '@/constants/regex'

import AuthorizeHeader from '@/pages/authorize/components/AuthorizeHeader.vue'
import { setBackendErrors } from '@/utils/errorApply'

defineOptions({
  name: 'AuthorizeRegister'
})

// composables
const { t } = useI18n()
const { mobile } = useDisplay()
const router = useRouter()

const errorMessages = {
  usernameIsRequired: t('$original.authorize.register.usernameIsRequired'),
  invalidUsernameLength: t(
    '$original.authorize.register.invalidUsernameLength',
    {
      min: 2,
      max: 8
    }
  ),
  usernameAlreadyUse: t('$original.authorize.register.usernameAlreadyUse'),
  passwordIsRequired: t('$original.authorize.register.passwordIsRequired'),
  invalidPasswordLength: t(
    '$original.authorize.register.invalidPasswordLength',
    {
      min: 8,
      max: 16
    }
  ),
  invalidPasswordFormat: t(
    '$original.authorize.register.invalidPasswordFormat'
  ),
  confirmPasswordIsRequired: t(
    '$original.authorize.register.confirmPasswordIsRequired'
  ),
  enteredPasswordsDiffer: t(
    '$original.authorize.register.enteredPasswordsDiffer'
  )
}

// states
const isPasswordVisible = ref(false)
const isConfirmPasswordVisible = ref(false)
const registerButtonLoading = ref(false)
const schema = yup.object({
  username: yup
    .string()
    .required(errorMessages.usernameIsRequired)
    .min(2, errorMessages.invalidUsernameLength)
    .max(8, errorMessages.invalidUsernameLength)
    .test(
      'unique-username',
      errorMessages.usernameAlreadyUse,
      async (value: string) => {
        if (!value || value.length < 2 || value.length > 8) return true
        try {
          const res = await debouncedCheckUsername(value)
          return res && !res.data
        } catch (error) {
          console.error(error || 'validate username is unique failed')
          return false
        }
      }
    ),
  password: yup
    .string()
    .required(errorMessages.passwordIsRequired)
    .min(8, errorMessages.invalidPasswordLength)
    .max(16, errorMessages.invalidPasswordLength)
    .matches(regex.password, errorMessages.invalidPasswordFormat),
  confirmPassword: yup
    .string()
    .required(errorMessages.confirmPasswordIsRequired)
    .oneOf([yup.ref('password')], errorMessages.enteredPasswordsDiffer)
})
const { handleSubmit, meta } = useForm<RegisterForm>({
  name: 'RegisterForm',
  validationSchema: toTypedSchema(schema),
  initialValues: {
    username: '',
    password: '',
    confirmPassword: ''
  }
})

const username = useField<string>('username')
const password = useField<string>('password')
const confirmPassword = useField<string>('confirmPassword')

// methods
const submit = handleSubmit((values, actions) => {
  if (meta.value.valid) {
    registerButtonLoading.value = true

    registerApi(values)
      .then(() => {
        // on success redirect to home
        router.push({
          name: 'authorize-login',
          query: { username: username.value.value }
        })
      })
      .catch((error) => {
        setBackendErrors<RegisterDto>(error, actions.setFieldError)
      })
      .finally(() => {
        registerButtonLoading.value = false
      })
  }
})

const debouncedCheckUsername = useDebounceFn(
  (username: string) => validateAuthorizeUsernameUniqueApi({ username }),
  500
)

const viewPrivacyPolicyAndTerms = () => {
  console.log('handler view privacy policy & terms')
}
</script>

<template>
  <div class="d-flex align-center justify-center mh-100 authorize-register">
    <v-card class="pa-4 authorize-card" :elevation="mobile ? 0 : 1">
      <!-- authorize header -->
      <authorize-header
        :subtitle="t('$original.authorize.register.subtitle')"
        :title="t('$original.authorize.register.title')"
      ></authorize-header>

      <!-- register form -->
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
            :label="t('$original.authorize.register.username')"
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
            :label="t('$original.authorize.register.password')"
            :type="isPasswordVisible ? 'text' : 'password'"
            variant="outlined"
            @click:append-inner="isPasswordVisible = !isPasswordVisible"
          />

          <!-- confirm password -->
          <v-text-field
            v-model="confirmPassword.value.value"
            :append-inner-icon="isConfirmPasswordVisible ? IconEye : IconEyeOff"
            autocomplete="off"
            base-color="input-border"
            :clearable="true"
            density="comfortable"
            :error-messages="confirmPassword.errorMessage.value"
            :label="t('$original.authorize.register.confirmPassword')"
            :type="isConfirmPasswordVisible ? 'text' : 'password'"
            variant="outlined"
            @click:append-inner="
              isConfirmPasswordVisible = !isConfirmPasswordVisible
            "
          />

          <!-- privacy policy and terms -->
          <v-checkbox class="d-flex mb-1" color="info" hide-details>
            <template #label>
              <span class="mr-1 i-agree">
                {{ t('$original.authorize.register.iAgree') }}
              </span>
              <span
                class="text-info opacity-100 privacy-policy-terms"
                @click.prevent="viewPrivacyPolicyAndTerms"
              >
                {{ t('$original.authorize.register.privacyPolicyAndTerms') }}
              </span>
            </template>
          </v-checkbox>

          <!-- submit button -->
          <v-btn
            :block="true"
            color="primary"
            :flat="true"
            height="44"
            :loading="registerButtonLoading"
            type="submit"
            variant="elevated"
          >
            {{ t('$original.authorize.register.register') }}
          </v-btn>

          <!-- login now -->
          <div class="d-flex align-center justify-end mt-4 mb-2">
            <span>
              {{ t('$original.authorize.register.alreadyHaveAccount') }}
            </span>
            <router-link
              class="text-info ml-1"
              :to="{ name: 'authorize-login' }"
            >
              {{ t('$original.authorize.register.loginNow') }}
            </router-link>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>
