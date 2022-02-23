export type SupportedMediaType = 'audio' | 'image'
export type SupportedSearchType = 'all' | SupportedMediaType
export type MediaType = 'audio' | 'image' | 'video'
export type SearchType = 'all' | MediaType
/**
 * The search result object
 */

type FrontendMediaType = MediaDetail['frontendMediaType']
export interface MediaResult<
  T extends
    | FrontendMediaType
    | FrontendMediaType[]
    | Record<string, FrontendMediaType>
> {
  result_count: number
  page_count: number
  page_size: number
  /**
   * This monstrosity maps media type keys like `image` or `audio` to a concrete model
   * We're doing this to make MediaService able to infer which type of media it's for
   * just based on the key (instead of a passed in type parameter, which isn't possible
   * with JSDoc and inference is always nicer to use when possible)
   */
  results: T extends FrontendMediaType
    ? DetailFromMediaType<T>
    : T extends Array<infer P>
    ? P extends FrontendMediaType
      ? DetailFromMediaType<P>[]
      : never
    : T extends Record<infer K, infer P>
    ? P extends FrontendMediaType
      ? Record<K, DetailFromMediaType<P>>
      : never
    : never
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

export interface Tag {
  name: string
  provider: [string]
}

export interface BaseMediaDetail<FrontendMediaType extends string> {
  id: string
  foreign_landing_url: string
  creator?: string
  creator_url?: string
  url: string
  title?: string
  license: string
  license_version: string
  license_url: string
  provider: string
  source?: string
  tags?: Tag[]
  attribution: string
  detail_url: string
  related_url: string
  thumbnail?: string
  frontendMediaType: FrontendMediaType
}

export interface AudioDetail extends BaseMediaDetail<'audio'> {
  audio_set?: any
  genres?: any
  duration?: number
  bit_rate?: number
  sample_rate?: number
  alt_files?: any
  filetype?: string
}

export interface ImageDetail extends BaseMediaDetail<'image'> {
  fields_matched?: string[]
}

export type MediaDetail = ImageDetail | AudioDetail

export type DetailFromMediaType<T extends MediaDetail['frontendMediaType']> =
  T extends 'image' ? ImageDetail : T extends 'audio' ? AudioDetail : never

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

export interface MediaStoreResult<T extends FrontendMediaType>
  extends MediaResult<Record<MediaDetail['id'], T>> {}

export interface MediaState {
  results: {
    audio: MediaStoreResult<'audio'>
    image: MediaStoreResult<'image'>
  }
  fetchState: {
    audio: FetchState
    image: FetchState
  }
  audio: AudioDetail
  image: ImageDetail
}

export interface MediaFetchState {
  isFetching: boolean
  fetchingError: string | null
  isFinished?: boolean
}
