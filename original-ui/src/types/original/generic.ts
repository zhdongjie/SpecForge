import type { Path, SubmissionContext } from 'vee-validate'
import type { App } from 'vue'
import type { RouteLocationRaw } from 'vue-router'

export type SetFieldErrorFn<T> = (
  field: Path<T>,
  message?: string | string[]
) => void
export type PluginInstallerFn = (app: App) => void

export interface TreeNode<T> {
  id: string
  parentId: string
  children: T[]
}

export interface TableHeader {
  title: string
  key: string
  sortable: boolean
  align: 'start' | 'end' | 'center'
}

export interface FormState<T> {
  values: T
  actions: SubmissionContext
}

export type ReplaceField<T, K extends keyof T, V> = Omit<T, K> & { [P in K]: V }

export interface BreadcrumbItem {
  title: string
  disabled: boolean
  to?: RouteLocationRaw
}
