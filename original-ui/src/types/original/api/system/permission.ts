export interface PermissionNodeVo {
  id: string
  parentId: string
  permissionName: string
  authority: string
  sort: number
  permissionType: string
  icon?: string | null
  linkAddress?: string | null
  linkTarget?: string | null
  routerPath?: string | null
  componentPath?: string | null
  keepAlive?: boolean | null
  visible: boolean
  permissionStatus: string
  createdTime?: string | null
  children: PermissionNodeVo[]
}
