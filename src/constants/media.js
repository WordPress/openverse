export const AUDIO = 'audio'
export const IMAGE = 'image'
export const VIDEO = 'video'
export const ALL_MEDIA = 'all'

/** @typedef {typeof AUDIO | typeof IMAGE | typeof VIDEO | typeof ALL_MEDIA} MediaType */

// Media types
/** @type {MediaType[]} */
export const mediaTypes = [AUDIO, IMAGE]
// Media types which support custom filters
/** @type {MediaType[]} */
export const supportedMediaTypes = [AUDIO, IMAGE, VIDEO]
/** @type {MediaType[]} */
export const allMediaTypes = [ALL_MEDIA, IMAGE, AUDIO, VIDEO]
