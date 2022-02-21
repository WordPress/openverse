export type SupportedMediaType = 'audio' | 'image'
export type SupportedSearchType = 'all' | SupportedMediaType
export type MediaType = 'audio' | 'image' | 'video'
export type SearchType = 'all' | MediaType
/**
 * The search result object
 */
export interface MediaResult<T> {
  result_count: number
  page_count: number
  page_size: number
  results: T
}

export type Query = {
  mediaType: SupportedMediaType
  q: string
  license: string
  license_type: string
  extension: string
  size: string
  aspect_ratio: string
  searchBy: string
  categories: string
  source: string
  duration: string
  mature: boolean
}

export type ApiQueryParams = {
  q: string
  license?: string
  license_type?: string
  extension?: string
  size?: string
  aspect_ratio?: string
  searchBy?: string
  categories?: string
  source?: string
  duration?: string
  mature?: string
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
  filetype?: string
  frontendMediaType?: 'audio'
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
  frontendMediaType?: 'image'
}

export interface FilterItem {
  code: string
  name: string
  checked: boolean
}

export interface Filters {
  licenses: FilterItem[]
  licenseTypes: FilterItem[]
  audioCategories: FilterItem[]
  imageCategories: FilterItem[]
  audioExtensions: FilterItem[]
  imageExtensions: FilterItem[]
  aspectRatios: FilterItem[]
  durations: FilterItem[]
  sizes: FilterItem[]
  audioProviders: FilterItem[]
  imageProviders: FilterItem[]
  searchBy: FilterItem[]
  mature: boolean
}

export interface FetchState {
  isFetching: boolean
  fetchingError: null | string
  isFinished?: boolean
}

export interface SearchState {
  searchType: SupportedSearchType
  query: Query
  filters: Filters
}

export interface ActiveMediaState {
  type: SupportedMediaType | null
  id: string | null
  status: 'ejected' | 'playing' | 'paused' // 'ejected' means player is closed
}

export interface MediaStoreResult {
  count: number
  page?: number
  pageCount: number
  items: { [key: SupportedMediaType]: AudioDetail | ImageDetail }
}

export interface MediaState {
  results: {
    audio: MediaStoreResult
    image: MediaStoreResult
  }
  fetchState: {
    audio: FetchState
    image: FetchState
  }
  audio: Object | AudioDetail
  image: Object | ImageDetail
}

export interface MediaFetchState {
  isFetching: boolean
  fetchingError: string | null
  isFinished?: boolean
}
