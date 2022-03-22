// We plan to remove this dependency, so don't need to add types for it:
// https://github.com/WordPress/openverse-frontend/issues/1103
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import clonedeep from 'lodash.clonedeep'

import { mediaFilterKeys } from '~/constants/filters'
import { ALL_MEDIA, SupportedSearchType } from '~/constants/media'

import { getParameterByName } from '~/utils/url-params'
import type {
  ApiQueryFilters,
  ApiQueryKeys,
  ApiQueryParams,
  FilterCategory,
  FilterItem,
  Filters,
  QueryKey,
} from '~/store/types'

const filterPropertyMappings: Record<FilterCategory, ApiQueryKeys> = {
  licenses: 'license',
  licenseTypes: 'license_type',
  audioCategories: 'categories',
  imageCategories: 'categories',
  audioExtensions: 'extension',
  imageExtensions: 'extension',
  durations: 'duration',
  aspectRatios: 'aspect_ratio',
  sizes: 'size',
  audioProviders: 'source',
  imageProviders: 'source',
  searchBy: 'searchBy',
  mature: 'mature',
}

const getMediaFilterTypes = (searchType: SupportedSearchType) => [
  ...mediaFilterKeys[searchType],
]
// {
//   license: 'cc0,pdm,by,by-sa,by-nc,by-nd,by-nc-sa,by-nc-nd',
//   imageCategories: 'photograph,illustration,digitized_artwork',
//   imageExtension: 'jpg,png',
//   aspect_ratio: 'square',
//   size: 'small',
//   source: 'animaldiversity,bio_diversity,brooklynmuseum,CAPL,clevelandmuseum,deviantart'
// }

/**
 * Joins all the filters which have the checked property `true`
 * to a string separated by commas for the API request URL, e.g.: "by,nd-nc,nc-sa".
 * Mature is a special case, and is converted to `true`.
 */
const filterToString = (filterItem: FilterItem[]) => {
  const filterString = filterItem
    .filter((f) => f.checked)
    .map((filterItem) => filterItem.code)
    .join(',')
  return filterString === 'mature' ? 'true' : filterString
}

/**
 * Converts the filter store object to the data format accepted by the API,
 * which has slightly different property names.
 * @param filters - object containing the filter data that comes from the filter store
 * @param searchType - search type for which API query should be created
 * @param hideEmpty - whether the query params with empty values should be removed
 * TODO: Refactor all of these 'reduce' calls to just use lodash methods :)
 */
export const filtersToQueryData = (
  filters: Filters,
  searchType: SupportedSearchType = ALL_MEDIA,
  hideEmpty = true
): ApiQueryFilters => {
  const mediaFilterTypes = getMediaFilterTypes(searchType)

  return mediaFilterTypes.reduce((query, filterCategory) => {
    const queryKey = filterPropertyMappings[filterCategory]
    const queryValue = filterToString(filters[filterCategory])
    if (queryValue || !hideEmpty) {
      query[queryKey] = queryValue
    }
    return query
  }, {} as ApiQueryFilters)
}

/**
 * Extract search type from the url. Returns the last part
 * of the path between `/search/` and query, or `all` by default.
 * `/search/?q=test`: all
 * `/search/image?q=test`: image
 * @param queryString - the query string from the url
 */
export const queryStringToSearchType = (
  queryString: string
): SupportedSearchType => {
  const searchTypePattern = /\/search\/(image|audio|video)\?*/
  const matchedType = queryString.match(searchTypePattern)
  return matchedType === null
    ? ALL_MEDIA
    : (matchedType[1] as SupportedSearchType)
}

/**
 * `source`, `extensions` and `categories` API parameters correspond
 * to different filters in different media types:
 * `source` - audioProviders/imageProviders
 * `extensions` - audioExtensions/imageExtensions
 * `categories` - audioCategories/imageCategories
 *
 * This function sets only filters that are possible for current
 * media type. E.g., for queryString `search/audio?extensions=ogg`
 * the `audioExtensions.ogg.checked` is set to true,
 * but for `search/images?extensions=ogg`, the extensions query parameter
 * is discarded, because `ogg` is not a valid extension for images.
 */
const getMediaTypeApiFilters = (
  filterParameter: string,
  parameterFilters: FilterItem[]
): FilterItem[] => {
  if (filterParameter !== '') {
    const parameterValues = filterParameter.split(',')
    parameterValues.forEach((parameter) => {
      const existingParameterIdx = parameterFilters.findIndex(
        (p) => p.code === parameter
      )
      if (existingParameterIdx > -1) {
        parameterFilters[existingParameterIdx] = {
          ...parameterFilters[existingParameterIdx],
          checked: true,
        }
      }
    })
  }
  return parameterFilters
}

/**
 * Converts the browser filter query string into the internal filter store data format.
 * For the API parameters that have the same name, but correspond to different filter categories
 * (`differentFiltersWithSameApiParams`), only the filters that exist for the selected search type
 * are used:
 * E.g. when the search type is `audio`, `extension=jpg,mp3` sets the audioExtensions mp3.checked to true,
 * and discards `jpg`.
 *
 * @param query - browser filter query
 * @param searchType - search type determines which filters are applied
 * @param defaultFilters - default filters for testing purposes
 */
export const queryToFilterData = ({
  query,
  searchType = 'image',
  defaultFilters,
}: {
  query: Record<string, string>
  searchType: SupportedSearchType
  defaultFilters: Partial<Filters>
}) => {
  // The default filterData object from search store doesn't contain provider filters,
  // so we can't use it.
  const filters = clonedeep(defaultFilters) as Filters
  const filterTypes = getMediaFilterTypes(searchType)
  const differentFiltersWithSameApiParams = [
    'audioProviders',
    'imageProviders',
    'audioExtensions',
    'imageExtensions',
    'audioCategories',
    'imageCategories',
  ]
  filterTypes.forEach((filterDataKey) => {
    if (differentFiltersWithSameApiParams.includes(filterDataKey)) {
      if (filterDataKey.startsWith(searchType)) {
        const parameter = query[filterPropertyMappings[filterDataKey]]
        if (parameter) {
          filters[filterDataKey] = getMediaTypeApiFilters(
            parameter,
            filters[filterDataKey]
          )
        }
      }
    } else {
      const queryDataKey = filterPropertyMappings[filterDataKey]
      if (query[queryDataKey]) {
        if (queryDataKey === 'mature' && query[queryDataKey].length > 0) {
          filters[filterDataKey][0].checked = true
        } else {
          const filterValues = query[queryDataKey].split(',')
          filterValues.forEach((val: string) => {
            const idx = filters[filterDataKey].findIndex((f) => f.code === val)
            if (idx >= 0) {
              filters[filterDataKey][idx].checked = true
            }
          })
        }
      }
    }
  })

  return filters
}

/**
 * converts the url query string to the data format accepted by the API.
 *
 * this is slightly different from filtersToQueryData as this converts the
 * query string and that converts the filter data.
 *
 * TODO: we might be able to refactor to eliminate the need for these two
 * separate functions.
 */
export const queryStringToQueryData = (queryString: string) => {
  const queryDataObject = {} as ApiQueryParams
  const searchType = queryStringToSearchType(queryString)
  const filterTypes = getMediaFilterTypes(searchType)
  filterTypes.forEach((filterDataKey) => {
    const queryDataKey = filterPropertyMappings[filterDataKey]
    queryDataObject[queryDataKey] = getParameterByName(
      queryDataKey,
      queryString
    )
  })
  queryDataObject.q = getParameterByName('q', queryString)

  return queryDataObject
}

/**
 * Compares two API queries, excluding the search term (`q`) parameter.
 */
export const areQueriesEqual = (
  newQuery: ApiQueryParams,
  oldQuery: ApiQueryParams
): boolean => {
  const queryKeys = (query: ApiQueryParams) =>
    Object.keys(query).filter((k) => k !== 'q') as QueryKey[]
  const oldQueryKeys = queryKeys(oldQuery)
  const newQueryKeys = queryKeys(newQuery)
  if (oldQueryKeys.length !== newQueryKeys.length) return false

  for (const key of oldQueryKeys) {
    if (oldQuery[key] !== newQuery[key]) {
      return false
    }
  }
  return true
}
