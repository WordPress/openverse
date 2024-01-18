import type { AudioDetail, ImageDetail } from "~/types/media"

export interface PaginatedApiResult {
  result_count: number
  page_count: number
  page_size: number
  page: number
}

export interface PaginatedApiMediaResult extends PaginatedApiResult {
  results: AudioDetail[] | ImageDetail[]
}
