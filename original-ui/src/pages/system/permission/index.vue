<script lang="ts" setup>
import type { PermissionNodeVo } from '@/types/original/api/system/permission'
import { IconRefresh, IconRoute, IconShield } from '@tabler/icons-vue'
import { enquiryPermissionTreeApi } from '@/api'

defineOptions({
  name: 'SystemPermissionManagement'
})

interface FlatPermissionNode extends PermissionNodeVo {
  depth: number
}

const loading = ref(false)
const permissionTree = ref<PermissionNodeVo[]>([])

const flattenTree = (
  nodes: PermissionNodeVo[],
  depth = 0
): FlatPermissionNode[] => {
  return nodes.flatMap((node) => [
    { ...node, depth },
    ...flattenTree(node.children || [], depth + 1)
  ])
}

const flatPermissions = computed(() => flattenTree(permissionTree.value))
const routePermissions = computed(
  () => flatPermissions.value.filter((item) => !!item.routerPath).length
)
const buttonPermissions = computed(
  () => flatPermissions.value.filter((item) => item.permissionType === 'BUTTON')
    .length
)

const loadPermissionTree = async () => {
  loading.value = true
  try {
    const { data } = await enquiryPermissionTreeApi()
    permissionTree.value = data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPermissionTree()
})
</script>

<template>
  <div class="d-flex flex-column ga-4">
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">Permission Nodes</div>
              <div class="text-h4 mt-2">{{ flatPermissions.length }}</div>
            </div>
            <icon-shield :size="28" class="text-primary" />
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="d-flex align-center justify-space-between">
            <div>
              <div class="text-overline">Route Surfaces</div>
              <div class="text-h4 mt-2">{{ routePermissions }}</div>
            </div>
            <icon-route :size="28" class="text-info" />
          </div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="pa-4">
          <div class="text-overline">Button Authorities</div>
          <div class="text-h4 mt-2">{{ buttonPermissions }}</div>
          <div class="text-medium-emphasis mt-1">
            Backed by <code>/v1/system/permission/tree</code>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="pa-4">
      <div class="d-flex align-center justify-space-between mb-4">
        <div>
          <div class="text-h6">Permission Tree</div>
          <div class="text-medium-emphasis">
            Template view for inspecting dynamic menu nodes and authority
            bindings.
          </div>
        </div>
        <v-btn
          :icon="true"
          size="small"
          variant="text"
          @click="loadPermissionTree"
        >
          <icon-refresh :size="18" />
        </v-btn>
      </div>

      <v-data-table
        :headers="[
          { title: 'Permission', key: 'permissionName', sortable: false },
          { title: 'Authority', key: 'authority', sortable: false },
          { title: 'Type', key: 'permissionType', sortable: false },
          { title: 'Router Path', key: 'routerPath', sortable: false },
          { title: 'Component Path', key: 'componentPath', sortable: false },
          { title: 'Status', key: 'permissionStatus', sortable: false }
        ]"
        :items="flatPermissions"
        :loading="loading"
      >
        <template #[`item.permissionName`]="{ item }">
          <div :style="{ paddingLeft: `${item.depth * 18}px` }">
            {{ item.permissionName }}
          </div>
        </template>
        <template #[`item.permissionType`]="{ item }">
          <v-chip size="small" variant="tonal">{{ item.permissionType }}</v-chip>
        </template>
        <template #[`item.permissionStatus`]="{ item }">
          <v-chip
            :color="item.permissionStatus === 'ENABLED' ? 'success' : 'warning'"
            size="small"
            variant="tonal"
          >
            {{ item.permissionStatus }}
          </v-chip>
        </template>
        <template #[`item.routerPath`]="{ item }">
          {{ item.routerPath || '-' }}
        </template>
        <template #[`item.componentPath`]="{ item }">
          {{ item.componentPath || '-' }}
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>
