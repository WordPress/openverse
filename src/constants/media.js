export const AUDIO = 'audio'
export const IMAGE = 'image'
export const VIDEO = 'video'
export const ALL_MEDIA = 'all'

/**
 * Media types that the API supports and this only includes 'real' media. ALL is a special case not used in this list.
 * These types also support custom filters.
 * Note: images should always be first here,
 *
 */
export const supportedMediaTypes = /** @type {const} */ ([IMAGE, AUDIO])

/**
 * The types of content that users can search. `All` is also an option here.
 */
export const supportedSearchTypes = /** @type {const} */ ([
  ALL_MEDIA,
  IMAGE,
  AUDIO,
])

/** @typedef {'supported'|'beta'|'additional'} SupportStatus */
export const statuses = /** @type {const} */ ({
  SUPPORTED: 'supported',
  BETA: 'beta',
  ADDITIONAL: 'additional',
})

/** @type {Record<import('~/store/types').SearchType, SupportStatus>} */
export const contentStatus = {
  [ALL_MEDIA]: statuses.SUPPORTED,
  [IMAGE]: statuses.SUPPORTED,
  [AUDIO]: statuses.BETA,
  [VIDEO]: statuses.ADDITIONAL,
}
