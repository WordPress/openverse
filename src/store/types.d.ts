/**
 * The search result object
 */
export interface MediaResult<T> {
  result_count: number
  page_count: number
  page_size: number
  results: T
}

/**
 * Audio Properties returned by the API
 */
export type AudioDetail = {
  id: string
  foreign_landing_url: string
  creator?: string
  creator_url?: string
  url: string
  license: string
  license_version: string
  license_url: string
  provider: string
  source?: string
  tags?: any
  attribution: string
  audio_set?: any
  genres?: any
  duration?: number
  bit_rate?: number
  sample_rate?: number
  alt_files?: any
  detail_url: string
  related_url: string
}

/**
 * Image Properties returned by the API
 */
export type ImageDetail = {
  id: string
  title?: string
  creator?: string
  creator_url?: string
  tags?: { name: string; provider: [string] }[]
  url: string
  thumbnail?: string
  provider: string
  source?: string
  license: string
  license_version: string
  license_url: string
  foreign_landing_url: string
  detail_url: string
  related_url: string
  fields_matched?: string[]
}

export interface ActiveMediaState {
  type: 'image' | 'audio' | null
  id: string | null
}
