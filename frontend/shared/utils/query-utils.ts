import type { SupportedMediaType } from "#shared/constants/media"

import type { LocationQueryValue } from "vue-router"

export const firstParam = (
  params: LocationQueryValue | LocationQueryValue[] | undefined
): string | null => {
  if (Array.isArray(params)) {
    return params[0]
  }
  return params ?? null
}

export function getNumber(
  params: LocationQueryValue | LocationQueryValue[] | undefined
): number {
  const value = firstParam(params)
  return value ? parseInt(value, 10) : -1
}

export function getString(
  params: LocationQueryValue | LocationQueryValue[] | undefined
): string {
  return firstParam(params) ?? ""
}

export const validateUUID = (id: string | undefined | null) => {
  if (!id) {
    return false
  }
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(
    id
  )
}

export const mediaSlug = (mediaType: SupportedMediaType) =>
  mediaType === "image" ? "images" : "audio"

/**
 * Create a query string for a single result page, e.g. `/search?q=term&p=1`.
 */
export const singleResultQuery = (searchTerm?: string, position?: number) => {
  if (!searchTerm && !position) {
    return ""
  }
  const query = new URLSearchParams()
  if (searchTerm) {
    query.set("q", searchTerm)
  }
  if (position) {
    query.set("p", position.toString())
  }
  return `?${query.toString()}`
}
