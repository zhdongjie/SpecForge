export interface DictionaryDataListVo {
  label: string
  value: string
  status: string
}

export interface DictionaryDataPageVo {
  id: string
  dictionaryTypeCode: string
  value: string
  label: string
  sort: number
  remark?: string | null
  createdTime: string
}

export interface DictionaryDataPageQuery {
  dictionaryTypeCode: string | null
  label: string | null
  value: string | null
  currentPage: number
  pageSize: number
  createdTimeStart: string | null
  createdTimeEnd: string | null
  orders: {
    key: string
    order: 'asc' | 'desc'
  }[]
}
