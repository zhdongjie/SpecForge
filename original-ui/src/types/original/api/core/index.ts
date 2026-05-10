export interface ResponseVo<T> {
  code: 20_000 | 40_000 | 40_100 | 40_300 | 50_000
  message: string
  data: T
  errors: FieldErrorVo[] | null
  timestamp: number
}

export interface FieldErrorVo {
  field: string
  errors: string[]
}

export interface PaginateVo<T> {
  total: number
  items: T[]
}

interface OrderDto {
  key: string
  order: 'asc' | 'desc'
}

export interface EnquiryConditionDto {
  createdTimeStart: string | null
  createdTimeEnd: string | null
  orders: OrderDto[]
}

export interface EnquiryPageDto extends EnquiryConditionDto {
  currentPage: number
  pageSize: number
}
