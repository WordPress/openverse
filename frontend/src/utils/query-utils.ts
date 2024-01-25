import { SupportedMediaType } from "~/constants/media"

import type { LocationQueryValue } from "vue-router"

export const firstParam = (
  params: LocationQueryValue | LocationQueryValue[]
): string | null => {
  if (Array.isArray(params)) {
    return params[0]
  }
  return params
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

export const DEFAULT_REQUEST_TIMEOUT = 30000
