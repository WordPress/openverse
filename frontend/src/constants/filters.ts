import { ALL_MEDIA, AUDIO, IMAGE, VIDEO, MODEL_3D } from "~/constants/media"
import { ACTIVE_LICENSES } from "~/constants/license"
import { deepFreeze } from "~/utils/deep-freeze"

import type { SearchType } from "~/constants/media"

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
  lengths: FilterItem[]
  sizes: FilterItem[]
  audioProviders: FilterItem[]
  imageProviders: FilterItem[]
}
export type FilterCategory = keyof Filters

/**
 * List of filters available for each search type. The order of the keys
 * is the same as in the filter checklist display (sidebar or modal).
 */
export const mediaFilterKeys = deepFreeze<Record<SearchType, FilterCategory[]>>(
  {
    [IMAGE]: [
      "licenseTypes",
      "licenses",
      "imageCategories",
      "imageExtensions",
      "aspectRatios",
      "sizes",
      "imageProviders",
    ],
    [AUDIO]: [
      "licenseTypes",
      "licenses",
      "audioCategories",
      "audioExtensions",
      "lengths",
      "audioProviders",
    ],
    [VIDEO]: [],
    [MODEL_3D]: [],
    [ALL_MEDIA]: ["licenseTypes", "licenses"],
  }
)

/**
 * A list of filters that are only used for the specific content type.
 * This is used to clear filters from other content types when changing the content type.
 */
export const mediaUniqueFilterKeys = deepFreeze<
  Record<SearchType, FilterCategory[]>
>({
  [ALL_MEDIA]: [],
  [IMAGE]: [
    "imageCategories",
    "imageExtensions",
    "aspectRatios",
    "sizes",
    "imageProviders",
  ],
  [AUDIO]: ["audioCategories", "audioExtensions", "lengths", "audioProviders"],
  [VIDEO]: [],
  [MODEL_3D]: [],
})

const filterCodesPerCategory = deepFreeze<Record<FilterCategory, string[]>>({
  licenses: [...ACTIVE_LICENSES],
  licenseTypes: ["commercial", "modification"],
  audioCategories: [
    "audiobook",
    "music",
    "news",
    "podcast",
    "pronunciation",
    "sound_effect",
  ],
  imageCategories: ["photograph", "illustration", "digitized_artwork"],
  audioExtensions: ["flac", "mid", "mp3", "oga", "ogg", "opus", "wav", "webm"],
  imageExtensions: ["jpg", "png", "gif", "svg"],
  aspectRatios: ["tall", "wide", "square"],
  lengths: ["shortest", "short", "medium", "long"],
  sizes: ["small", "medium", "large"],
  audioProviders: [],
  imageProviders: [],
})
/**
 * Converts the filterCodesPerCategory object into the format that's used by the filter store.
 * Name is used as the i18n $t key.
 * ```
 * {
 *   "audioCategories": [
 *     {
 *       "code": "music",
 *       "name": "filters.audioCategories.music",
 *       "checked": false
 *     }, ...
 *   ],
 * }
 *```
 */
export const initFilters = () =>
  Object.entries(filterCodesPerCategory).reduce(
    (acc, [filterType, filters]) => ({
      ...acc,
      [filterType]: filters.map((item) => ({
        code: item,
        name: `filters.${filterType}.${item}`,
        checked: false,
      })),
    }),
    {} as Filters
  )

export const filterData = deepFreeze(initFilters())
