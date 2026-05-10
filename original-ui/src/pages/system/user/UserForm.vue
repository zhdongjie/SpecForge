<script lang="ts" setup>
import type { PropType } from 'vue'
import type { DictionaryDataListVo } from '@/types/original/api/system/dictionaryData'
import type { RoleListVo } from '@/types/original/api/system/role'
import type { UpdateUserDto, UserForm } from '@/types/original/api/system/user'
import type { FormState } from '@/types/original/generic'
import { toTypedSchema } from '@vee-validate/yup'
import { useField, useForm } from 'vee-validate'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import * as yup from 'yup'
import {
  enquiryDictionaryDataListApi,
  enquiryRoleListApi,
  validateUserUsernameUniqueApi,
  validateUserEmailUniqueApi,
  validateUserPhoneNumberUniqueApi
} from '@/api'
import regex from '@/constants/regex'

defineOptions({
  name: 'UserForm'
})

// props
const componentProps = defineProps({
  initData: {
    type: Object as PropType<UpdateUserDto>,
    required: false,
    default: undefined
  },
  confirmLoading: {
    type: Boolean as PropType<boolean>,
    required: false,
    default: false
  },
  confirmBtnColor: {
    type: String as PropType<string>,
    required: false,
    default: 'primary'
  }
})

const initUser = componentProps.initData

// emits
const emits = defineEmits<{
  close: []
  complete: [formState: FormState<UserForm>]
}>()
// const model = useVModel(componentProps, 'user', emits) as Ref<FormUser>

// composables
const { t } = useI18n()

// error message
const errorMessages = {
  usernameIsRequired: t('$original.system.management.user.usernameIsRequired'),
  invalidUsernameLength: t(
    '$original.system.management.user.invalidUsernameLength',
    {
      min: 2,
      max: 8
    }
  ),
  usernameAlreadyUse: t('$original.system.management.user.usernameAlreadyUse'),
  invalidEmailLength: t('$original.system.management.user.invalidEmailLength', {
    max: 256
  }),
  invalidEmailFormat: t('$original.system.management.user.invalidEmailFormat'),
  emailAlreadyExists: t('$original.system.management.user.emailAlreadyExists'),
  invalidPhoneNumberFormat: t(
    '$original.system.management.user.invalidPhoneNumberFormat'
  ),
  phoneNumberAlreadyExists: t(
    '$original.system.management.user.phoneNumberAlreadyExists'
  ),
  invalidBirthday: t('$original.system.management.user.invalidBirthday'),
  roleListIsRequired: t('$original.system.management.user.roleListIsRequired'),
  passwordIsRequired: t('$original.system.management.user.passwordIsRequired'),
  invalidPasswordLength: t(
    '$original.system.management.user.invalidPasswordLength',
    {
      min: 8,
      max: 16
    }
  ),
  invalidPasswordFormat: t(
    '$original.system.management.user.invalidPasswordFormat'
  )
}
const schema = yup.object({
  id: yup.string().nullable(),
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
  email: yup
    .string()
    .nullable()
    .max(256, errorMessages.invalidEmailLength)
    .matches(regex.email, errorMessages.invalidEmailFormat)
    .test(
      'unique-email',
      errorMessages.emailAlreadyExists,
      async (value?: string | null) => {
        if (!value || !regex.email.test(value)) return true
        try {
          const res = await debouncedCheckEmail(value)
          return res && !res.data
        } catch (error) {
          console.error(error || 'validate email is unique failed')
          return false
        }
      }
    ),

  phoneNumber: yup
    .string()
    .nullable()
    .matches(regex.phoneNumber, errorMessages.invalidPhoneNumberFormat)
    .test(
      'unique-phone-number',
      errorMessages.phoneNumberAlreadyExists,
      async (value?: string | null) => {
        if (!value || !regex.phoneNumber.test(value)) return true
        try {
          const res = await debouncedCheckPhoneNumber(value)
          return res && !res.data
        } catch (error) {
          console.error(error || 'validate phone number is unique failed')
          return false
        }
      }
    ),

  gender: yup.string().nullable(),

  birthday: yup
    .date()
    .nullable()
    .max(new Date(), errorMessages.invalidBirthday),

  roleIds: yup
    .array()
    .of(yup.string())
    .min(1, errorMessages.roleListIsRequired)
    .required(errorMessages.roleListIsRequired)
    .ensure(),

  password: yup
    .string()
    .nullable()
    .when('id', {
      is: (user: UpdateUserDto | undefined) => !user,
      then: (schema) =>
        schema
          .required(errorMessages.passwordIsRequired)
          .min(8, errorMessages.invalidPasswordLength)
          .max(16, errorMessages.invalidPasswordLength)
          .matches(regex.password, errorMessages.invalidPasswordFormat)
    })
})
const { handleSubmit, resetForm, meta } = useForm<UserForm>({
  name: 'UserForm',
  validationSchema: toTypedSchema(schema),
  initialValues: {
    id: initUser?.id || undefined,
    username: initUser?.username || '',
    email: initUser?.email || null,
    phoneNumber: initUser?.phoneNumber || null,
    gender: initUser?.gender || null,
    // v-date-input 内部会将 string 转换为 Date 类型
    birthday: initUser?.birthday ? new Date(initUser?.birthday) : null,
    roleIds: initUser?.roleIds || [],
    password: undefined
  }
})
const username = useField<string>('username')
const email = useField<string | null>('email')
const phoneNumber = useField<string | null>('phoneNumber')
const gender = useField<string | null>('gender')
const birthday = useField<Date | null>('birthday')
const roleIds = useField<string[]>('roleIds')
const password = useField<string | undefined>('password')

// states
const isPasswordVisible = ref<boolean>(false)
const rolesOptions = ref<RoleListVo[]>([])
const genderOptions = ref<DictionaryDataListVo[]>([])

// mounted
onMounted(async () => {
  // load role options
  await loadRoleList()

  // load gender options
  await loadGenderList()
})

// methods
const submit = handleSubmit((values, actions) => {
  if (meta.value.valid) {
    emits('complete', {
      values,
      actions
    })
  }
})

const loadRoleList = async () => {
  const { data: roleList } = await enquiryRoleListApi()
  rolesOptions.value = roleList
}

const loadGenderList = async () => {
  const { data: roleList } =
    await enquiryDictionaryDataListApi('system_user_gender')
  genderOptions.value = roleList
}

const debouncedCheckUsername = useDebounceFn(
  (username: string) =>
    validateUserUsernameUniqueApi({ id: initUser?.id, username }),
  500
)

const debouncedCheckEmail = useDebounceFn(
  (email: string) => validateUserEmailUniqueApi({ id: initUser?.id, email }),
  500
)

const debouncedCheckPhoneNumber = useDebounceFn(
  (phoneNumber: string) =>
    validateUserPhoneNumberUniqueApi({ id: initUser?.id, phoneNumber }),
  500
)

// reset form
const handleResetForm = () => {
  resetForm()
  isPasswordVisible.value = false
}
</script>

<template>
  <v-form @submit.prevent="submit">
    <v-row class="pt-4">
      <!-- username -->
      <v-col class="py-0" cols="12" sm="6">
        <v-text-field
          v-model="username.value.value"
          autocomplete="off"
          base-color="input-border"
          :clearable="true"
          density="comfortable"
          :error-messages="username.errorMessage.value"
          :label="t('$original.system.management.user.username')"
          variant="outlined"
        />
      </v-col>

      <!-- email -->
      <v-col class="py-0" cols="12" sm="6">
        <v-text-field
          v-model="email.value.value"
          autocomplete="off"
          base-color="input-border"
          :clearable="true"
          density="comfortable"
          :error-messages="email.errorMessage.value"
          :label="t('$original.system.management.user.email')"
          variant="outlined"
        />
      </v-col>

      <!-- phone number -->
      <v-col class="py-0" cols="12" sm="6">
        <v-text-field
          v-model="phoneNumber.value.value"
          autocomplete="off"
          base-color="input-border"
          :clearable="true"
          density="comfortable"
          :error-messages="phoneNumber.errorMessage.value"
          :label="t('$original.system.management.user.phoneNumber')"
          variant="outlined"
        />
      </v-col>

      <!-- gender -->
      <v-col class="py-0" cols="12" sm="6">
        <v-select
          v-model="gender.value.value"
          base-color="input-border"
          :clearable="true"
          density="comfortable"
          :error-messages="gender.errorMessage.value"
          item-title="label"
          :items="genderOptions"
          :label="t('$original.system.management.user.gender')"
          :list-props="{ nav: true, density: 'compact' }"
          variant="outlined"
        >
          <template #selection="{ item }">
            <span>{{ item.raw.label }}</span>
          </template>
          <template #item="{ props, item }">
            <v-list-item
              :disabled="item.raw.status === 'DISABLED'"
              v-bind="props"
            >
              <template #title>
                <div class="text-body-1">{{ item.title }}</div>
              </template>
            </v-list-item>
          </template>
        </v-select>
      </v-col>

      <!-- birthday -->
      <v-col class="py-0" cols="12" sm="6">
        <v-date-input
          v-model="birthday.value.value"
          base-color="input-border"
          :clearable="true"
          density="comfortable"
          :error-messages="birthday.errorMessage.value"
          :label="t('$original.system.management.user.birthday')"
          prepend-icon=""
          variant="outlined"
        />
      </v-col>

      <!-- roles -->
      <v-col class="py-0" cols="12" sm="6">
        <v-select
          v-model="roleIds.value.value"
          autocomplete="off"
          base-color="input-border"
          :clearable="true"
          density="comfortable"
          :error-messages="roleIds.errorMessage.value"
          item-title="roleName"
          item-value="id"
          :items="rolesOptions"
          :label="t('$original.system.management.user.role')"
          :list-props="{ nav: true, density: 'compact' }"
          multiple
          variant="outlined"
        >
          <template #selection="{ item, index }">
            <v-chip v-show="index < 1" size="x-small">
              <span>{{ item.raw.roleName }}</span>
            </v-chip>
            <span v-show="index === 1" class="text-caption">
              (+{{ roleIds.value.value.length - 1 }})
            </span>
          </template>
          <template #item="{ props, item }">
            <v-list-item
              v-bind="props"
              :disabled="item.raw.status === 'DISABLED'"
            >
              <template #title>
                <div class="text-body-1">{{ item.title }}</div>
              </template>
              <template #prepend="{ isSelected, select }">
                <v-checkbox-btn
                  class="text-body-1"
                  density="comfortable"
                  :model-value="isSelected"
                  @update:model-value="select"
                ></v-checkbox-btn>
              </template>
            </v-list-item>
          </template>
        </v-select>
      </v-col>

      <!-- password -->
      <v-col class="py-0" cols="12" sm="6">
        <v-text-field
          v-if="!initData"
          v-model="password.value.value"
          :append-inner-icon="
            isPasswordVisible ? 'mdi:mdi-eye' : 'mdi:mdi-eye-off'
          "
          autocomplete="off"
          base-color="input-border"
          :clearable="true"
          density="comfortable"
          :error-messages="password.errorMessage.value"
          :label="t('$original.system.management.user.password')"
          :type="isPasswordVisible ? 'text' : 'password'"
          variant="outlined"
          @click:append-inner="isPasswordVisible = !isPasswordVisible"
        />
      </v-col>

      <v-col class="text-right" cols="12">
        <!-- cancel button -->
        <v-btn
          class="mr-2"
          height="36"
          size="small"
          variant="tonal"
          width="80"
          @click="emits('close')"
        >
          {{ t('$original.common.cancel') }}
        </v-btn>

        <!-- reset button -->
        <v-btn
          class="mr-2"
          :disabled="confirmLoading"
          height="36"
          size="small"
          variant="tonal"
          width="80"
          @click="handleResetForm"
        >
          {{ t('$original.common.reset') }}
        </v-btn>

        <!-- confirm button -->
        <v-btn
          :color="confirmBtnColor"
          height="36"
          :loading="confirmLoading"
          size="small"
          type="submit"
          variant="flat"
          width="80"
        >
          {{ t('$original.common.confirm') }}
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>
