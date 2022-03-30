/* Media types */

export const IMAGE = 'image'
export const AUDIO = 'audio'
export const VIDEO = 'video'
export const MODEL_3D = 'model_3d'
export const ALL_MEDIA = 'all'

/**
 * all existing media types
 */
export const mediaTypes = [IMAGE, AUDIO, VIDEO, MODEL_3D] as const

export type MediaType = typeof mediaTypes[number]

/**
 * real media types that the API supports;
 * - `ALL_MEDIA` is not an option here.
 * - These types also support custom filters.
 * - `IMAGE` should always be first here.
 */
export const supportedMediaTypes = [IMAGE, AUDIO] as const

export type SupportedMediaType = typeof supportedMediaTypes[number]

export const searchTypes = [ALL_MEDIA, ...mediaTypes] as const

export type SearchType = typeof searchTypes[number]

/**
 * the types of content that users can search; `ALL_MEDIA` is also a valid
 * option here.
 */
export const supportedSearchTypes = [ALL_MEDIA, ...supportedMediaTypes] as const

export type SupportedSearchType = typeof supportedSearchTypes[number]

/* Media support */

const SUPPORTED = 'supported' // Native search
const BETA = 'beta' // Native but incomplete search
const ADDITIONAL = 'additional' // Meta search

export const contentStatus = Object.freeze({
  [ALL_MEDIA]: SUPPORTED,
  [IMAGE]: SUPPORTED,
  [AUDIO]: BETA,
  [VIDEO]: ADDITIONAL,
} as const)
