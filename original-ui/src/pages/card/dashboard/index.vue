<script lang="ts" setup>
import { IconCards, IconRefresh } from '@tabler/icons-vue'
import { meApi } from '@/api'

defineOptions({
  name: 'CardWorkspaceDashboard'
})

const loading = ref(false)
const routeCount = ref(0)
const buttonCount = ref(0)
const username = ref('-')

const loadSummary = async () => {
  loading.value = true
  try {
    const { data } = await meApi()
    username.value = data.username
    routeCount.value = data.routers.length
    buttonCount.value = data.buttons.length
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
        <div class="text-h6">Card Workspace Dashboard</div>
        <div class="text-medium-emphasis">
          Lightweight dashboard template backed by the menu contract.
        </div>
      </div>
      <v-btn :icon="true" size="small" variant="text" @click="loadSummary">
        <icon-refresh :size="18" />
      </v-btn>
    </div>

    <v-row>
      <v-col cols="12" md="4">
        <v-card class="pa-4" variant="tonal" color="secondary">
          <div class="text-overline">Current Operator</div>
          <div class="text-h5 mt-2">{{ username }}</div>
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
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">Granted Buttons</div>
              <div class="text-h4 mt-2">{{ buttonCount }}</div>
            </div>
            <icon-cards :size="26" class="text-primary" />
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
</template>
