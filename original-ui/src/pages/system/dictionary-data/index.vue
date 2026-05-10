<script lang="ts" setup>
import type {
  DictionaryDataListVo,
  DictionaryDataPageQuery,
  DictionaryDataPageVo
} from '@/types/original/api/system/dictionaryData'
import type {
  DictionaryTypePageQuery,
  DictionaryTypePageVo
} from '@/types/original/api/system/dictionaryType'
import { IconRefresh } from '@tabler/icons-vue'
import {
  enquiryDictionaryDataListApi,
  enquiryDictionaryTypePageApi
} from '@/api'
import request from '@/plugins/axios'
import type { PaginateVo } from '@/types/original/api/core'

defineOptions({
  name: 'SystemDictionaryDataManagement'
})

const loading = ref(false)
const optionLoading = ref(false)
const typeOptions = ref<DictionaryTypePageVo[]>([])
const optionItems = ref<DictionaryDataListVo[]>([])
const items = ref<DictionaryDataPageVo[]>([])
const total = ref(0)
const query = reactive<DictionaryDataPageQuery>({
  dictionaryTypeCode: null,
  label: null,
  value: null,
  currentPage: 1,
  pageSize: 20,
  createdTimeStart: null,
  createdTimeEnd: null,
  orders: [{ key: 'createdTime', order: 'desc' }]
})

const typeQuery = reactive<DictionaryTypePageQuery>({
  dictionaryTypeName: null,
  dictionaryTypeCode: null,
  currentPage: 1,
  pageSize: 100,
  createdTimeStart: null,
  createdTimeEnd: null,
  orders: [{ key: 'sort', order: 'asc' }]
})

const enquiryDictionaryDataPageApi = (payload: DictionaryDataPageQuery) => {
  return request.get<DictionaryDataPageQuery, PaginateVo<DictionaryDataPageVo>>(
    '/v1/system/dictionary-data/page',
    payload
  )
}

const loadDictionaryTypes = async () => {
  const { data } = await enquiryDictionaryTypePageApi(typeQuery)
  typeOptions.value = data.items
  if (!query.dictionaryTypeCode && data.items.length > 0) {
    query.dictionaryTypeCode = data.items[0].dictionaryTypeCode
  }
}

const loadOptionList = async () => {
  if (!query.dictionaryTypeCode) {
    optionItems.value = []
    return
  }

  optionLoading.value = true
  try {
    const { data } = await enquiryDictionaryDataListApi(query.dictionaryTypeCode)
    optionItems.value = data
  } finally {
    optionLoading.value = false
  }
}

const loadPage = async () => {
  loading.value = true
  try {
    const { data } = await enquiryDictionaryDataPageApi(query)
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

const reloadAll = async () => {
  await loadDictionaryTypes()
  await Promise.all([loadPage(), loadOptionList()])
}

watch(
  () => query.dictionaryTypeCode,
  () => {
    query.currentPage = 1
    loadPage()
    loadOptionList()
  }
)

onMounted(() => {
  reloadAll()
})
</script>

<template>
  <div class="d-flex flex-column ga-4">
    <v-card class="pa-4">
      <div class="d-flex align-center justify-space-between mb-4">
        <div>
          <div class="text-h6">Dictionary Data Management</div>
          <div class="text-medium-emphasis">
            Bound to <code>/v1/system/dictionary-data/page</code> and
            <code>/v1/system/dictionary-data/list/{dictionaryTypeCode}</code>
          </div>
        </div>
        <v-btn :icon="true" size="small" variant="text" @click="reloadAll">
          <icon-refresh :size="18" />
        </v-btn>
      </div>

      <v-row class="mb-2">
        <v-col cols="12" md="4">
          <v-select
            v-model="query.dictionaryTypeCode"
            clearable
            hide-details
            item-title="dictionaryTypeName"
            item-value="dictionaryTypeCode"
            :items="typeOptions"
            label="Dictionary Type"
            variant="outlined"
          ></v-select>
        </v-col>
        <v-col cols="12" md="4">
          <v-text-field
            v-model="query.label"
            clearable
            hide-details
            label="Label"
            variant="outlined"
            @keyup.enter="loadPage"
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="4">
          <v-text-field
            v-model="query.value"
            clearable
            hide-details
            label="Value"
            variant="outlined"
            @keyup.enter="loadPage"
          ></v-text-field>
        </v-col>
      </v-row>
    </v-card>

    <v-card class="pa-4">
      <div class="text-subtitle-1 mb-3">Current Option Surface</div>
      <div v-if="optionLoading" class="text-medium-emphasis">Loading options...</div>
      <div v-else class="d-flex flex-wrap ga-2">
        <v-chip
          v-for="option in optionItems"
          :key="`${option.value}-${option.label}`"
          size="small"
          variant="tonal"
        >
          {{ option.label }} / {{ option.value }}
        </v-chip>
      </div>
    </v-card>

    <v-card class="pa-4">
      <v-data-table-server
        v-model:items-per-page="query.pageSize"
        v-model:page="query.currentPage"
        :headers="[
          { title: '#', key: 'index', sortable: false },
          { title: 'Type Code', key: 'dictionaryTypeCode', sortable: false },
          { title: 'Label', key: 'label', sortable: false },
          { title: 'Value', key: 'value', sortable: false },
          { title: 'Sort', key: 'sort', sortable: false },
          { title: 'Created Time', key: 'createdTime', sortable: false }
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
      </v-data-table-server>
    </v-card>
  </div>
</template>
