/**
 * The search result object
 */
import type { FetchState } from '~/composables/use-fetch-state'

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

export interface Query {
  q: string
  license_type: string
  license: string
  extension: string
  size: string
  aspect_ratio: string
  searchBy: string
  categories: string
  source: string
  duration: string
  mature: string
}
export type QueryKey = keyof Query

export interface ApiQueryParams {
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
export type ApiQueryFilters = Omit<ApiQueryParams, 'q'>
export type ApiQueryKeys = keyof ApiQueryFilters

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
  audio_set?: string
  genres?: string[]
  duration?: number
  bit_rate?: number
  sample_rate?: number
  alt_files?: { provider: string; filetype: string }[]
  filetype?: string
  peaks?: number[]
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
  mature: FilterItem[]
}
export type FilterCategory = keyof Filters

export type MediaStoreResult<T extends FrontendMediaType> = MediaResult<
  Record<MediaDetail['id'], T>
>

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
