import type { LocationQueryValue } from "vue-router"

export const firstParam = (
  params: LocationQueryValue | LocationQueryValue[]
) => {
  if (Array.isArray(params)) {
    return params[0]
  }
  return params
}
