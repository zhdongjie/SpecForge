<script lang="ts" setup>
import type { PermissionNodeVo } from '@/types/original/api/system/permission'
import { IconFolder, IconRefresh, IconRoute } from '@tabler/icons-vue'
import { enquiryPermissionTreeApi, meApi } from '@/api'

defineOptions({
  name: 'SystemProjectConsole'
})

const loading = ref(false)
const username = ref('-')
const routeCount = ref(0)
const permissionCount = ref(0)
const topModules = ref<PermissionNodeVo[]>([])

const loadConsole = async () => {
  loading.value = true
  try {
    const [{ data: profile }, { data: tree }] = await Promise.all([
      meApi(),
      enquiryPermissionTreeApi()
    ])
    username.value = profile.username
    routeCount.value = profile.routers.length
    permissionCount.value = profile.buttons.length
    topModules.value = tree.filter((item) => item.permissionType !== 'FUNCTION')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadConsole()
})
</script>

<template>
  <div class="d-flex flex-column ga-4">
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">Project Console</div>
              <div class="text-h5 mt-2">{{ username }}</div>
            </div>
            <icon-folder :size="28" class="text-primary" />
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="text-overline">Visible Routes</div>
          <div class="text-h4 mt-2">{{ routeCount }}</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="text-overline">Granted Button Authorities</div>
          <div class="text-h4 mt-2">{{ permissionCount }}</div>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="pa-4">
      <div class="d-flex align-center justify-space-between mb-4">
        <div>
          <div class="text-h6">Template Control Surface</div>
          <div class="text-medium-emphasis">
            This page is a standard template console backed by current
            permission and personal-center contracts.
          </div>
        </div>
        <v-btn :icon="true" size="small" variant="text" @click="loadConsole">
          <icon-refresh :size="18" />
        </v-btn>
      </div>

      <v-list>
        <v-list-item
          v-for="module in topModules"
          :key="module.id"
          :title="module.permissionName"
          :subtitle="module.authority"
        >
          <template #prepend>
            <icon-route :size="18" class="mr-2 text-info" />
          </template>
          <template #append>
            <v-chip size="small" variant="tonal">
              {{ module.permissionType }}
            </v-chip>
          </template>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>
