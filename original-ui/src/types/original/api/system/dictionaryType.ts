import type { EnquiryPageDto } from '@/types/original/api/core'

export interface DictionaryTypePageQuery extends EnquiryPageDto {
  dictionaryTypeName: string | null
  dictionaryTypeCode: string | null
}

export interface DictionaryTypePageVo {
  id: string
  dictionaryTypeName: string
  dictionaryTypeCode: string
  sort: number
  dictionaryTypeStatus: string
  remark?: string | null
}

export interface DictionaryTypeListVo {
  id: string
  dictionaryTypeName: string
  dictionaryTypeCode: string
}
