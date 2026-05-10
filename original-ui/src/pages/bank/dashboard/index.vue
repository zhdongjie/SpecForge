<script lang="ts" setup>
import { IconRefresh, IconTrendingUp } from '@tabler/icons-vue'
import { meApi } from '@/api'

defineOptions({
  name: 'BankWorkspaceDashboard'
})

const loading = ref(false)
const username = ref('-')
const roles = ref<string[]>([])
const buttons = ref<string[]>([])

const loadSummary = async () => {
  loading.value = true
  try {
    const { data } = await meApi()
    username.value = data.username
    roles.value = data.roles
    buttons.value = data.buttons
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadSummary()
})
</script>

<template>
  <v-card class="pa-4">
    <div class="d-flex align-center justify-space-between mb-4">
      <div>
        <div class="text-h6">Bank Workspace Dashboard</div>
        <div class="text-medium-emphasis">
          Summary page backed by the personal-center contract.
        </div>
      </div>
      <v-btn :icon="true" size="small" variant="text" @click="loadSummary">
        <icon-refresh :size="18" />
      </v-btn>
    </div>

    <v-row>
      <v-col cols="12" md="4">
        <v-card class="pa-4" variant="tonal" color="primary">
          <div class="text-overline">Operator</div>
          <div class="text-h5 mt-2">{{ username }}</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="text-overline">Role Coverage</div>
          <div class="text-h4 mt-2">{{ roles.length }}</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">Action Authorities</div>
              <div class="text-h4 mt-2">{{ buttons.length }}</div>
            </div>
            <icon-trending-up :size="26" class="text-success" />
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>
