import type { Path } from 'vee-validate'
import type { ResponseVo } from '@/types/original/api/core'
import type { SetFieldErrorFn } from '@/types/original/generic'

export const setBackendErrors = <T>(
  error: ResponseVo<null>,
  setFieldError: SetFieldErrorFn<T>
) => {
  const backendErrors = error?.errors
  if (Array.isArray(backendErrors)) {
    for (const fieldError of backendErrors) {
      const field = fieldError.field
      if (fieldError.errors.length > 0) {
        setFieldError(field as Path<T>, fieldError.errors.join(', '))
      }
    }
  }
}
