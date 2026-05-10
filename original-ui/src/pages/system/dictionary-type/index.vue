<script lang="ts" setup>
import type {
  DictionaryTypePageQuery,
  DictionaryTypePageVo
} from '@/types/original/api/system/dictionaryType'
import { IconRefresh } from '@tabler/icons-vue'
import { enquiryDictionaryTypePageApi } from '@/api'

defineOptions({
  name: 'SystemDictionaryTypeManagement'
})

const loading = ref(false)
const items = ref<DictionaryTypePageVo[]>([])
const total = ref(0)
const query = reactive<DictionaryTypePageQuery>({
  dictionaryTypeName: null,
  dictionaryTypeCode: null,
  currentPage: 1,
  pageSize: 20,
  createdTimeStart: null,
  createdTimeEnd: null,
  orders: [{ key: 'sort', order: 'asc' }]
})

const loadPage = async () => {
  loading.value = true
  try {
    const { data } = await enquiryDictionaryTypePageApi(query)
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPage()
})
</script>

<template>
  <v-card class="pa-4">
    <div class="d-flex align-center justify-space-between mb-4">
      <div>
        <div class="text-h6">Dictionary Type Management</div>
        <div class="text-medium-emphasis">
          Bound to <code>/v1/system/dictionary-type/page</code>
        </div>
      </div>
      <v-btn :icon="true" size="small" variant="text" @click="loadPage">
        <icon-refresh :size="18" />
      </v-btn>
    </div>

    <v-row class="mb-2">
      <v-col cols="12" md="4">
        <v-text-field
          v-model="query.dictionaryTypeName"
          clearable
          hide-details
          label="Dictionary Type Name"
          variant="outlined"
          @keyup.enter="loadPage"
        ></v-text-field>
      </v-col>
      <v-col cols="12" md="4">
        <v-text-field
          v-model="query.dictionaryTypeCode"
          clearable
          hide-details
          label="Dictionary Type Code"
          variant="outlined"
          @keyup.enter="loadPage"
        ></v-text-field>
      </v-col>
      <v-col cols="12" md="4" class="d-flex align-center">
        <v-btn color="primary" variant="tonal" @click="loadPage">Search</v-btn>
      </v-col>
    </v-row>

    <v-data-table-server
      v-model:items-per-page="query.pageSize"
      v-model:page="query.currentPage"
      :headers="[
        { title: '#', key: 'index', sortable: false },
        { title: 'Name', key: 'dictionaryTypeName', sortable: false },
        { title: 'Code', key: 'dictionaryTypeCode', sortable: false },
        { title: 'Sort', key: 'sort', sortable: false },
        { title: 'Status', key: 'dictionaryTypeStatus', sortable: false },
        { title: 'Remark', key: 'remark', sortable: false }
      ]"
      :items="items"
      :items-length="total"
      :items-per-page-options="[10, 20, 50]"
      :loading="loading"
      @update:options="loadPage"
    >
      <template #[`item.index`]="{ index }">
        {{ index + 1 + (query.currentPage - 1) * query.pageSize }}
      </template>
      <template #[`item.dictionaryTypeStatus`]="{ item }">
        <v-chip size="small" variant="tonal">{{ item.dictionaryTypeStatus }}</v-chip>
      </template>
      <template #[`item.remark`]="{ item }">
        {{ item.remark || '-' }}
      </template>
    </v-data-table-server>
  </v-card>
</template>
