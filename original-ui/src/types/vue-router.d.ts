import type { Layout } from '@/types/original/config'
import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    dynamic?: boolean
    title: string
    layout: Layout
    redirectIfLoggedIn?: boolean
  }
}
