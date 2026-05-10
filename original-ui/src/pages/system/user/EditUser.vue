<script lang="ts" setup>
import type { PropType } from 'vue'
import type {
  UpdateUserDto,
  UserForm as UserFormType
} from '@/types/original/api/system/user'
import type { FormState } from '@/types/original/generic'
import { IconX } from '@tabler/icons-vue'
import { format } from 'date-fns'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { editUserApi, enquiryUserDetailsApi } from '@/api'
// components
import UserForm from '@/pages/system/user/UserForm.vue'

import { setBackendErrors } from '@/utils/errorApply'

defineOptions({
  name: 'EditUser'
})

// props
const componentProps = defineProps({
  userId: {
    type: String as PropType<string>,
    required: true
  }
})

// emits
const emits = defineEmits(['close', 'success'])

// states
const user = ref<UpdateUserDto>({
  id: '',
  username: '',
  birthday: null,
  email: null,
  gender: null,
  phoneNumber: null,
  roleIds: []
})

// states
const editUserButtonLoading = ref<boolean>(false)

// composables
const { t } = useI18n()

// mounted
onMounted(() => {
  loadUserDetails()
})

// methods
const loadUserDetails = () => {
  const userId = componentProps.userId

  if (userId) {
    enquiryUserDetailsApi(userId).then((response) => {
      const { data: userDetails } = response
      user.value = userDetails
    })
  }
}

const handlerEditUser = (formState: FormState<UserFormType>) => {
  editUserButtonLoading.value = true

  const values = formState.values
  const apiValues: UpdateUserDto = {
    ...values,
    birthday: values.birthday ? format(values.birthday, 'yyyy-MM-dd') : null
  }

  editUserApi(apiValues)
    .then(() => {
      emits('success')
    })
    .catch((error) => {
      setBackendErrors(error, formState.actions.setFieldError)
    })
    .finally(() => {
      editUserButtonLoading.value = false
    })
}
</script>

<template>
  <v-card>
    <!-- title -->
    <v-toolbar color="warning" density="compact">
      <v-toolbar-title class="text-subtitle-1">
        {{ t('$original.system.management.user.editUser') }}
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
          :key="user.id"
          confirm-btn-color="warning"
          :confirm-loading="editUserButtonLoading"
          :init-data="user"
          @close="emits('close')"
          @complete="handlerEditUser($event)"
        ></user-form>
      </v-container>
    </v-card-text>
  </v-card>
</template>
