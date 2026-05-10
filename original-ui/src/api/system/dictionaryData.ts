import type { DictionaryDataListVo } from '@/types/original/api/system/dictionaryData'
import request from '@/plugins/axios'

const enquiryDictionaryDataListApi = (dictionaryTypeCode: string) => {
  return request.get<null, DictionaryDataListVo[]>(
    `/v1/system/dictionary-data/list/${dictionaryTypeCode}`
  )
}

export { enquiryDictionaryDataListApi }
