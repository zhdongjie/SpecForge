import type { PaginateVo } from '@/types/original/api/core'
import type {
  DictionaryTypeListVo,
  DictionaryTypePageQuery,
  DictionaryTypePageVo
} from '@/types/original/api/system/dictionaryType'
import request from '@/plugins/axios'

const enquiryDictionaryTypePageApi = (query: DictionaryTypePageQuery) => {
  return request.get<DictionaryTypePageQuery, PaginateVo<DictionaryTypePageVo>>(
    '/v1/system/dictionary-type/page',
    query
  )
}

const enquiryDictionaryTypeListApi = () => {
  return request.get<null, DictionaryTypeListVo[]>(
    '/v1/system/dictionary-type/list'
  )
}

export { enquiryDictionaryTypeListApi, enquiryDictionaryTypePageApi }
