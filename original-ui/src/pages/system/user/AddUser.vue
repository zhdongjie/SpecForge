<script lang="ts" setup>
import type {
  CreateUserDto,
  UserForm as UserFormType
} from '@/types/original/api/system/user'
import type { FormState } from '@/types/original/generic'
import { IconX } from '@tabler/icons-vue'
import { format } from 'date-fns'

import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { createUserApi } from '@/api'
// components
import UserForm from '@/pages/system/user/UserForm.vue'
import { setBackendErrors } from '@/utils/errorApply'

defineOptions({
  name: 'AddUser'
})

// emits
const emits = defineEmits(['close', 'success'])

// states
const addUserButtonLoading = ref<boolean>(false)

// composables
const { t } = useI18n()

// methods
const handlerAddUser = (formState: FormState<UserFormType>) => {
  addUserButtonLoading.value = true

  const values = formState.values
  const apiValues: CreateUserDto = {
    ...values,
    birthday: values.birthday ? format(values.birthday, 'yyyy-MM-dd') : null
  }

  createUserApi(apiValues)
    .then(() => {
      emits('success')
    })
    .catch((error) => {
      setBackendErrors(error, formState.actions.setFieldError)
    })
    .finally(() => {
      addUserButtonLoading.value = false
    })
}
</script>

<template>
  <v-card>
    <!-- title -->
    <v-toolbar color="secondary" density="compact">
      <v-toolbar-title class="text-subtitle-1">
        {{ t('$original.system.management.user.addUser') }}
      </v-toolbar-title>
      <template #append>
        <v-btn class="mr-4" :icon="true" size="x-small" @click="emits('close')">
          <icon-x :size="16"></icon-x>
        </v-btn>
      </template>
    </v-toolbar>

    <v-card-text>
      <v-container>
        <user-form
          confirm-btn-color="secondary"
          :confirm-loading="addUserButtonLoading"
          @close="emits('close')"
          @complete="handlerAddUser($event)"
        ></user-form>
      </v-container>
    </v-card-text>
  </v-card>
</template>
