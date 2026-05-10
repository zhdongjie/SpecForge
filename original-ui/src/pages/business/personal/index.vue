<script lang="ts" setup>
import type {
  ChangePasswordDto,
  MeVo
} from '@/types/original/api/business/personal'
import { IconLockPassword, IconRefresh, IconRoute } from '@tabler/icons-vue'
import { changePasswordApi, meApi } from '@/api'
import { toast } from 'vuetify-sonner'

defineOptions({
  name: 'BusinessPersonalCenter'
})

const loading = ref(false)
const submitting = ref(false)
const profile = ref<MeVo | null>(null)
const passwordForm = ref<ChangePasswordDto>({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const visibleRoutes = computed(() => profile.value?.routers ?? [])
const visibleButtons = computed(() => profile.value?.buttons ?? [])

const loadProfile = async () => {
  loading.value = true
  try {
    const { data } = await meApi()
    profile.value = data
  } finally {
    loading.value = false
  }
}

const submitPasswordChange = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    toast.error('The new password and confirm password must match.')
    return
  }

  submitting.value = true
  try {
    await changePasswordApi(passwordForm.value)
    toast.success('Password updated successfully.')
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<template>
  <div class="d-flex flex-column ga-4">
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="text-overline">Current User</div>
          <div class="text-h5 mt-2">{{ profile?.username || '-' }}</div>
          <div class="text-medium-emphasis mt-1">
            Created at {{ profile?.createdTime || '-' }}
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">Visible Routes</div>
              <div class="text-h4 mt-2">{{ visibleRoutes.length }}</div>
            </div>
            <icon-route :size="28" class="text-info" />
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">Granted Buttons</div>
              <div class="text-h4 mt-2">{{ visibleButtons.length }}</div>
            </div>
            <icon-lock-password :size="28" class="text-primary" />
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" lg="7">
        <v-card class="pa-4 h-100">
          <div class="d-flex align-center justify-space-between mb-4">
            <div>
              <div class="text-h6">Profile Surface</div>
              <div class="text-medium-emphasis">
                Bound to <code>/v1/business/personal/me</code>
              </div>
            </div>
            <v-btn :icon="true" size="small" variant="text" @click="loadProfile">
              <icon-refresh :size="18" />
            </v-btn>
          </div>

          <v-list lines="two">
            <v-list-item title="Username" :subtitle="profile?.username || '-'"></v-list-item>
            <v-list-item title="Roles">
              <template #subtitle>
                <div class="d-flex flex-wrap ga-2 mt-1">
                  <v-chip
                    v-for="role in profile?.roles || []"
                    :key="role"
                    size="small"
                    variant="tonal"
                  >
                    {{ role }}
                  </v-chip>
                </div>
              </template>
            </v-list-item>
            <v-list-item title="Email" :subtitle="profile?.email || '-'"></v-list-item>
            <v-list-item
              title="Phone Number"
              :subtitle="profile?.phoneNumber || '-'"
            ></v-list-item>
          </v-list>

          <v-divider class="my-4" />

          <div class="text-subtitle-1 mb-3">Visible Routers</div>
          <v-table density="compact">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Router Path</th>
                <th>Component Path</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="router in visibleRoutes" :key="router.id">
                <td>{{ router.name }}</td>
                <td>{{ router.type }}</td>
                <td>{{ 'routerPath' in router ? router.routerPath : '-' }}</td>
                <td>
                  {{ 'componentPath' in router ? router.componentPath : '-' }}
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>

      <v-col cols="12" lg="5">
        <v-card class="pa-4 h-100">
          <div class="text-h6 mb-1">Change Password</div>
          <div class="text-medium-emphasis mb-4">
            Bound to <code>/v1/business/personal/password</code>
          </div>

          <v-form @submit.prevent="submitPasswordChange">
            <v-text-field
              v-model="passwordForm.oldPassword"
              autocomplete="current-password"
              class="mb-2"
              label="Old Password"
              type="password"
              variant="outlined"
            ></v-text-field>
            <v-text-field
              v-model="passwordForm.newPassword"
              autocomplete="new-password"
              class="mb-2"
              label="New Password"
              type="password"
              variant="outlined"
            ></v-text-field>
            <v-text-field
              v-model="passwordForm.confirmPassword"
              autocomplete="new-password"
              class="mb-4"
              label="Confirm Password"
              type="password"
              variant="outlined"
            ></v-text-field>

            <v-btn
              color="primary"
              :loading="submitting"
              type="submit"
              variant="tonal"
            >
              Submit Password Change
            </v-btn>
          </v-form>

          <v-divider class="my-4" />

          <div class="text-subtitle-1 mb-3">Granted Buttons</div>
          <div class="d-flex flex-wrap ga-2">
            <v-chip
              v-for="button in visibleButtons"
              :key="button"
              size="small"
              variant="outlined"
            >
              {{ button }}
            </v-chip>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
