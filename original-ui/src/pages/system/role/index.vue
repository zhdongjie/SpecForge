<script lang="ts" setup>
import type { RoleListVo } from '@/types/original/api/system/role'
import { IconRefresh, IconShieldCheck, IconUser } from '@tabler/icons-vue'
import { enquiryRoleListApi } from '@/api'

defineOptions({
  name: 'SystemRoleManagement'
})

const loading = ref(false)
const roles = ref<RoleListVo[]>([])

const loadRoles = async () => {
  loading.value = true
  try {
    const { data } = await enquiryRoleListApi()
    roles.value = data
  } finally {
    loading.value = false
  }
}

const totalRoles = computed(() => roles.value.length)
const enabledRoles = computed(
  () => roles.value.filter((role) => role.status === 'ENABLED').length
)

onMounted(() => {
  loadRoles()
})
</script>

<template>
  <div class="d-flex flex-column ga-4">
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="text-overline">Role Inventory</div>
          <div class="text-h4 mt-2">{{ totalRoles }}</div>
          <div class="text-medium-emphasis mt-1">Available role definitions</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">Enabled Roles</div>
              <div class="text-h4 mt-2">{{ enabledRoles }}</div>
            </div>
            <icon-shield-check :size="28" class="text-success" />
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">Default Surface</div>
              <div class="text-h6 mt-2">Role list contract</div>
              <div class="text-medium-emphasis mt-1">
                Bound to <code>/v1/system/role/list</code>
              </div>
            </div>
            <icon-user :size="28" class="text-primary" />
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="pa-4">
      <div class="d-flex align-center justify-space-between mb-4">
        <div>
          <div class="text-h6">Role Management</div>
          <div class="text-medium-emphasis">
            This template currently binds the role list surface for dynamic menu
            and permission smoke validation.
          </div>
        </div>
        <v-btn :icon="true" size="small" variant="text" @click="loadRoles">
          <icon-refresh :size="18" />
        </v-btn>
      </div>

      <v-data-table
        :headers="[
          { title: '#', key: 'index', sortable: false, align: 'center' },
          { title: 'Role ID', key: 'id', sortable: false },
          { title: 'Role Name', key: 'roleName', sortable: false },
          { title: 'Status', key: 'status', sortable: false }
        ]"
        :items="roles"
        :loading="loading"
      >
        <template #[`item.index`]="{ index }">
          {{ index + 1 }}
        </template>
        <template #[`item.status`]="{ item }">
          <v-chip
            :color="item.status === 'ENABLED' ? 'success' : 'warning'"
            size="small"
            variant="tonal"
          >
            {{ item.status }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>
