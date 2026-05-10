import type { Icon } from '@tabler/icons-vue'
import type {
  CardWith,
  ContentLayout,
  ContentWidth,
  Language,
  RouterTransition,
  Theme
} from '@/types/original/config'

export type LanguageOption = { label: string; value: Language }
export type ContentLayoutOption = { value: ContentLayout; icon: Icon }
export type ContentWidthOption = { value: ContentWidth; icon: Icon }
export type SidebarTypeOption = { value: boolean; icon: Icon }
export type CardWithOption = { value: CardWith; icon: Icon }
export type MenuGroupOpenOnOption = { value: boolean; icon: Icon }
export type RouterTransitionOption = RouterTransition
export type PageSizeOption = { title: string; value: number }
export type ThemeOption = {
  title: string
  items: { value: Theme; color: string }[]
}

export type OptionsCode =
  | 'system_language_code'
  | 'system_role_status'
  | 'system_permission_type'
  | 'system_permission_link_target'
  | 'system_permission_status'
  | 'system_file_type_size_unit'
  | 'system_file_type_status'
  | 'system_file_metadata_status'
  | 'system_scheduled_task_group'
  | 'system_scheduled_misfire_policy'
  | 'system_scheduled_task_status'
  | 'system_dictionary_type_status'
  | 'system_dictionary_data_status'
  | 'system_user_gender'
