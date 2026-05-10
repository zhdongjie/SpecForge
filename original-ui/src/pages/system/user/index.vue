<script lang="ts" setup>
import type { RoleListVo } from '@/types/original/api/system/role'
import type {
  EnquiryUserPageDto,
  UserPageVo
} from '@/types/original/api/system/user'
import type { TableHeader } from '@/types/original/generic'
import {
  IconDownload,
  IconEdit,
  IconPlus,
  IconRefresh,
  IconReload,
  IconSearch,
  IconTrash,
  IconUpload,
  IconX
} from '@tabler/icons-vue'
import { useDisplay } from 'vuetify'
import { toast } from 'vuetify-sonner'
import { deleteUserApi, enquiryRoleListApi, enquiryUserPageApi } from '@/api'
import appConfig from '@/appConfig'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { pageSizeOptions } from '@/constants/options'
import AddUser from '@/pages/system/user/AddUser.vue'
import EditUser from '@/pages/system/user/EditUser.vue'
import { useField, useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/yup'
import * as yup from 'yup'

defineOptions({
  name: 'SystemUserManagement'
})

// states
const rolesOptions = ref<RoleListVo[]>([])
const addUserDialogVisible = ref<boolean>(false)
const users = ref<UserPageVo[]>([])
const total = ref<number>(0)
const tableLoading = ref<boolean>(false)
const selectedUsers = ref<UserPageVo[]>([])
const deleteUserId = ref<string>('')
const deleteUserName = ref<string>('')
const deleteUserPromptDialogVisible = ref<boolean>(false)
const editUserId = ref<string>('')
const editUserDialogVisible = ref<boolean>(false)
const schema = yup.object({
  username: yup.string().nullable(),
  roleIds: yup.array().of(yup.string()).ensure(),
  currentPage: yup.number().nullable(),
  pageSize: yup.number().nullable(),
  orders: yup
    .array()
    .of(
      yup.object({
        key: yup.string().required(),
        order: yup.string().oneOf(['asc', 'desc']).required()
      })
    )
    .ensure(),
  createdTimeStart: yup.date().nullable(),
  createdTimeEnd: yup.date().nullable()
})
const { values, handleSubmit, resetForm } = useForm<EnquiryUserPageDto>({
  name: 'SearchUserForm',
  validationSchema: toTypedSchema(schema),
  initialValues: {
    username: '',
    roleIds: [],
    currentPage: 1,
    pageSize: 20,
    orders: [
      {
        key: 'createdTime',
        order: 'asc'
      }
    ],
    createdTimeStart: null,
    createdTimeEnd: null
  }
})

const username = useField<string | null>('username')
const roleIds = useField<string[]>('roleIds')

const currentPage = useField<number>('currentPage')
const pageSize = useField<number>('pageSize')
const orders = useField<{ key: string; order: 'asc' | 'desc' }[]>('orders')

// composables
const { t } = useI18n()
const { xs, mobile } = useDisplay()

// mounted
onMounted(() => {
  // load role options
  loadRoleList()
})

// computed
const dialogIsFullscreen = computed(() => {
  return xs.value
})

const deleteConfirmMessage = computed(() => {
  if (deleteUserId.value) {
    return t('$original.system.management.user.deleteUserConfirm', {
      username: deleteUserName.value
    })
  } else {
    return t('$original.system.management.user.deleteBatchConfirm', {
      count: selectedUsers.value.length
    })
  }
})

// methods
const loadUsers = handleSubmit((values) => {
  // open table loading
  tableLoading.value = true

  enquiryUserPageApi(values)
    .then((response) => {
      const { data: userPaginate } = response

      // total user numbers
      total.value = userPaginate.total
      // current page users
      users.value = userPaginate.items
    })
    .catch((error) => {
      toast.error(error.message, {
        action: {
          buttonProps: {
            icon: IconX,
            size: 'small'
          }
        }
      })
    })
    .finally(() => {
      tableLoading.value = false
    })
})

function handleResetForm() {
  resetForm({
    values: {
      ...values,
      username: '',
      roleIds: [],
      createdTimeStart: null,
      createdTimeEnd: null
    }
  })

  loadUsers()
}

const handlerDeleteUserPrompt = (user?: UserPageVo) => {
  if (user) {
    deleteUserId.value = user.id
    deleteUserName.value = user.username || ''
  } else {
    deleteUserId.value = ''
    deleteUserName.value = ''
  }

  // open delete user prompt dialog
  deleteUserPromptDialogVisible.value = true
}
const openEditUserDialog = (userId: string) => {
  editUserId.value = userId

  editUserDialogVisible.value = true
}
const handlerAddUserSuccess = () => {
  // close create user dialog
  addUserDialogVisible.value = false

  // reload users
  loadUsers()
}
const loadRoleList = async () => {
  const { data: roleList } = await enquiryRoleListApi()
  rolesOptions.value = roleList
}

const headers = ref<TableHeader[]>([
  { title: '#', key: 'index', align: 'center', sortable: false },
  {
    title: t('$original.system.management.user.avatar'),
    key: 'avatar',
    align: 'center',
    sortable: false
  },
  {
    title: t('$original.system.management.user.username'),
    key: 'username',
    align: 'center',
    sortable: false
  },
  {
    title: t('$original.system.management.user.email'),
    key: 'email',
    align: 'center',
    sortable: false
  },
  {
    title: t('$original.system.management.user.phoneNumber'),
    key: 'phoneNumber',
    align: 'center',
    sortable: false
  },
  {
    title: t('$original.system.management.user.gender'),
    key: 'gender',
    align: 'center',
    sortable: false
  },
  {
    title: t('$original.system.management.user.role'),
    key: 'roles',
    align: 'center',
    sortable: false
  },
  {
    title: t('$original.common.createdTime'),
    key: 'createdTime',
    align: 'center',
    sortable: true
  },
  {
    title: t('$original.common.actions'),
    key: 'actions',
    sortable: false,
    align: 'center'
  }
])

const getColor = (role: string) => {
  if (role === 'Admin' || role === '管理员') return 'error'
  if (role === 'User' || role === '用户') return 'info'
  return ''
}

const handlerEditUserSuccess = () => {
  // close edit user dialog
  editUserDialogVisible.value = false

  // reload users
  loadUsers()
}

const handlerDeleteUser = () => {
  const userIds: string[] = []

  if (deleteUserId.value) {
    // delete individual
    userIds.push(deleteUserId.value)
  } else {
    // batch delete
    for (const item of selectedUsers.value) {
      userIds.push(item.id)
    }
  }

  if (userIds.length > 0) {
    // call delete user API
    deleteUserApi(userIds)
      .then(() => {
        // deselect deleted users
        selectedUsers.value = selectedUsers.value.filter(
          (user) => !userIds.includes(user.id)
        )

        // reload users
        loadUsers()

        // Show success message
        toast.success(t('$original.system.management.user.deleteSuccess'), {
          action: {
            buttonProps: {
              icon: IconX,
              size: 'small'
            }
          }
        })
      })
      .catch((error) => {
        toast.error(error.message, {
          action: {
            buttonProps: {
              icon: IconX,
              size: 'small'
            }
          }
        })
      })
      .finally(() => {
        deleteUserId.value = ''
        deleteUserName.value = ''
        // close delete user prompt dialog
        deleteUserPromptDialogVisible.value = false
      })
  }
}
</script>

<template>
  <v-card class="pa-4 system-user-management-container">
    <!-- search form -->
    <v-card-text>
      <v-form @submit.prevent="loadUsers">
        <v-row>
          <!-- username or email -->
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="username.value.value"
              autocomplete="off"
              base-color="input-border"
              :clearable="true"
              density="compact"
              hide-details
              :label="t('$original.system.management.user.username')"
              variant="outlined"
            ></v-text-field>
          </v-col>

          <!-- roles -->
          <v-col cols="12" sm="4">
            <v-select
              v-model="roleIds.value.value"
              autocomplete="off"
              base-color="input-border"
              :clearable="true"
              density="compact"
              hide-details
              item-title="roleName"
              item-value="id"
              :items="rolesOptions"
              :label="t('$original.system.management.user.role')"
              :list-props="{
                nav: true,
                density: 'compact'
              }"
              multiple
              variant="outlined"
            >
              <template #selection="{ item, index }">
                <v-chip
                  v-if="index < 1"
                  size="x-small"
                  :text="item.title"
                ></v-chip>
                <span
                  v-if="index === 1"
                  class="text-grey text-caption align-self-center"
                >
                  (+{{ roleIds.value.value.length - 1 }})
                </span>
              </template>
              <template #item="{ props, item }">
                <v-list-item v-bind="props">
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
          <v-col cols="12" sm="4">
            <v-btn
              class="mr-2"
              color="primary"
              height="40"
              size="small"
              type="submit"
              variant="tonal"
            >
              <template #prepend>
                <icon-search size="18" />
              </template>
              {{ t('$original.common.search') }}
            </v-btn>

            <v-btn
              color="info"
              height="40"
              size="small"
              variant="tonal"
              @click="handleResetForm"
            >
              <template #prepend>
                <icon-reload size="18" />
              </template>
              {{ t('$original.common.reset') }}
            </v-btn>
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>

    <v-card-text>
      <!-- action button -->
      <v-row>
        <v-col class="d-flex align-center justify-space-between" :cols="12">
          <div>
            <v-dialog
              v-model="addUserDialogVisible"
              :fullscreen="dialogIsFullscreen"
              :persistent="true"
              :width="dialogIsFullscreen ? '100vw' : '800px'"
            >
              <template #activator="{ props }">
                <!-- add user button -->
                <v-btn
                  v-bind="props"
                  class="mr-2 mb-2"
                  color="secondary"
                  height="30"
                  size="small"
                  width="90"
                >
                  <v-icon :start="true">
                    <icon-plus :size="14"></icon-plus>
                  </v-icon>
                  {{ t('$original.common.add') }}
                </v-btn>
              </template>

              <add-user
                @close="addUserDialogVisible = false"
                @success="handlerAddUserSuccess"
              />
            </v-dialog>

            <!-- batch delete user button -->
            <v-btn
              class="mr-2 mb-2"
              color="error"
              :disabled="selectedUsers.length === 0"
              height="30"
              size="small"
              width="90"
              @click="handlerDeleteUserPrompt()"
            >
              <v-icon :start="true">
                <icon-trash :size="14"></icon-trash>
              </v-icon>
              {{ t('$original.common.delete') }}
            </v-btn>

            <!-- import user button -->
            <v-btn
              class="mr-2 mb-2"
              color="info"
              height="30"
              size="small"
              width="90"
            >
              <v-icon :start="true">
                <icon-upload :size="14"></icon-upload>
              </v-icon>
              {{ t('$original.common.import') }}
            </v-btn>

            <!-- export user button -->
            <v-btn
              class="mb-2"
              color="warning"
              height="30"
              size="small"
              width="90"
            >
              <v-icon :start="true">
                <icon-download :size="14"></icon-download>
              </v-icon>
              {{ t('$original.common.export') }}
            </v-btn>
          </div>

          <v-btn
            class="mb-2"
            :icon="true"
            size="small"
            variant="flat"
            @click="loadUsers()"
          >
            <icon-refresh :size="18"></icon-refresh>
          </v-btn>
        </v-col>
      </v-row>

      <v-data-table-server
        v-model="selectedUsers"
        v-model:items-per-page="pageSize.value.value"
        v-model:page="currentPage.value.value"
        v-model:sort-by="orders.value.value"
        color="primary"
        fixed-header
        :headers="headers"
        hover
        :items="users"
        :items-length="total"
        :items-per-page-options="pageSizeOptions"
        :loading="tableLoading"
        :mobile="mobile"
        return-object
        select-strategy="all"
        show-select
        @update:options="loadUsers()"
      >
        <!-- index -->
        <template #[`item.index`]="{ index }">
          {{ index + 1 }}
        </template>

        <!-- avatar -->
        <template #[`item.avatar`]="{ item }">
          <img
            alt="avatar"
            class="rounded-circle img-fluid my-4"
            :src="item.avatar || appConfig.avatar"
            width="46"
          />
        </template>

        <!-- email -->
        <template #[`item.email`]="{ item }">
          <copy-label v-if="item.email" :text="item.email" />
          <div v-else>{{ '-' }}</div>
        </template>

        <!-- phone number -->
        <template #[`item.phoneNumber`]="{ item }">
          <copy-label v-if="item.phoneNumber" :text="item.phoneNumber" />
          <div v-else>{{ '-' }}</div>
        </template>

        <!-- gender -->
        <template #[`item.gender`]="{ item }">
          {{ item.gender || '-' }}
        </template>

        <!-- roles -->
        <template #[`item.roles`]="{ item }">
          <v-chip
            v-for="(role, index) in item.roles"
            :key="role"
            :base-color="getColor(role)"
            :class="{ 'mr-1': index !== item.roles.length - 1 }"
            size="small"
            variant="tonal"
          >
            {{ role }}
          </v-chip>
        </template>

        <!-- actions -->
        <template #[`item.actions`]="{ item }">
          <!-- edit -->
          <v-btn
            color="warning"
            :icon="true"
            size="small"
            variant="text"
            @click="openEditUserDialog(item.id)"
          >
            <icon-edit :size="18"></icon-edit>
          </v-btn>

          <!-- delete -->
          <v-btn
            color="error"
            :icon="true"
            size="small"
            variant="text"
            @click="handlerDeleteUserPrompt(item)"
          >
            <icon-trash :size="18"></icon-trash>
          </v-btn>
        </template>
      </v-data-table-server>
    </v-card-text>

    <!-- edit user dialog -->
    <v-dialog
      v-model="editUserDialogVisible"
      :fullscreen="dialogIsFullscreen"
      :persistent="true"
      :width="dialogIsFullscreen ? '100vw' : '800px'"
    >
      <edit-user
        :user-id="editUserId"
        @close="editUserDialogVisible = false"
        @success="handlerEditUserSuccess"
      ></edit-user>
    </v-dialog>

    <!-- delete user prompt dialog -->
    <confirm-dialog
      v-model="deleteUserPromptDialogVisible"
      :title="t('$original.common.warning')"
      :message="deleteConfirmMessage"
      :confirm-button-text="t('$original.common.confirm')"
      :cancel-button-text="t('$original.common.cancel')"
      confirm-button-color="error"
      @confirm="handlerDeleteUser"
    />
  </v-card>
</template>
