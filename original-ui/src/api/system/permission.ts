import type { PermissionNodeVo } from '@/types/original/api/system/permission'
import request from '@/plugins/axios'

const enquiryPermissionTreeApi = () => {
  return request.get<null, PermissionNodeVo[]>('/v1/system/permission/tree')
}

export { enquiryPermissionTreeApi }
