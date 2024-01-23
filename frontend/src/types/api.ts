import type { AudioDetail, ImageDetail } from "~/types/media"

export interface PaginatedApiResult {
  result_count: number
  page_count: number
  page_size: number
  page: number
}

// TODO: `null` and `undefined` should not be allowed here, but they are returned by the API.
export interface PaginatedApiMediaResult extends PaginatedApiResult {
  results: AudioDetail[] | ImageDetail[] | null | undefined
}
