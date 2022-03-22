import { supportedSearchTypes } from '~/constants/media'

/**
 * Validates the search types that have supported API endpoints.
 * This means that ALL_MEDIA is invalid because it is basically
 * a combination of all other supported API media types.
 * Any future search type that is not fully supported (video, 3d)
 * will also be invalid.
 */
export const isValidSearchType = (v) => supportedSearchTypes.includes(v)
