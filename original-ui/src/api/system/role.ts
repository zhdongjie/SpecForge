import type { RoleListVo } from '@/types/original/api/system/role'
import request from '@/plugins/axios'

const enquiryRoleListApi = () => {
  return request.get<null, RoleListVo[]>('/v1/system/role/list')
}

export { enquiryRoleListApi }
