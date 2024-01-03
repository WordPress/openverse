import {
  FilterCategory,
  FilterItem,
  Filters,
  mediaFilterKeys,
} from "~/constants/filters"
import {
  ALL_MEDIA,
  mediaTypes,
  SearchType,
  SupportedSearchType,
  supportedSearchTypes,
} from "~/constants/media"
import { INCLUDE_SENSITIVE_QUERY_PARAM } from "~/constants/content-safety"
import { deepClone } from "~/utils/clone"

import {
  SearchFilterKeys,
  PaginatedSearchQuery,
  SearchFilterQuery,
} from "~/types/search"

import { firstParam } from "~/utils/query-utils"

import type { Context } from "@nuxt/types"
import type { Dictionary } from "vue-router/types/router"

/**
 * This maps properties in the search store state to the corresponding API query
 * parameters. The convention is that filter property names are plural, and API query
 * parameters are singular.
 */
const filterPropertyMappings: Record<FilterCategory, SearchFilterKeys> = {
  licenses: "license",
  licenseTypes: "license_type",
  audioCategories: "category",
  imageCategories: "category",
  audioExtensions: "extension",
  imageExtensions: "extension",
  lengths: "length",
  aspectRatios: "aspect_ratio",
  sizes: "size",
  audioProviders: "source",
  imageProviders: "source",
}

const getMediaFilterTypes = (searchType: SearchType) => {
  return supportedSearchTypes.includes(searchType as SupportedSearchType)
    ? [...mediaFilterKeys[searchType]]
    : []
}

/**
 * Joins all the filters which have the checked property `true`
 * to a string separated by commas for the API request URL, e.g.: "by,nd-nc,nc-sa".
 * `includeSensitiveResults` is a special case, and is converted to `true`.
 */
const filterToString = (filterItem: FilterItem[]) => {
  const filterString = filterItem
    .filter((f) => f.checked)
    .map((filterItem) => filterItem.code)
    .join(",")
  return filterString === INCLUDE_SENSITIVE_QUERY_PARAM ? "true" : filterString
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
  searchType: Parameters<typeof getMediaFilterTypes>[0] = ALL_MEDIA,
  hideEmpty = true
) => {
  const mediaFilterTypes = getMediaFilterTypes(searchType)

  return mediaFilterTypes.reduce((query, filterCategory) => {
    const queryKey = filterPropertyMappings[filterCategory]
    const queryValue = filterToString(filters[filterCategory])
    if (queryValue || !hideEmpty) {
      query[queryKey] = queryValue
    }
    return query
  }, {} as SearchFilterQuery)
}

/**
 * Extract search type from the url. Returns the last part
 * of the path after `/search/`, or `all` by default.
 * `/search/`: all
 * `/search/image`: image
 * @param path - the path string from the url
 */
export const pathToSearchType = (path: string): SearchType => {
  const searchTypePattern = new RegExp(`/search/(${mediaTypes.join("|")})`)
  const matchedType = path.match(searchTypePattern)
  return matchedType === null ? ALL_MEDIA : (matchedType[1] as SearchType)
}

/**
 * `source`, `extension` and `category` API parameters correspond
 * to different filters in different media types:
 * `source` - audioProviders/imageProviders
 * `extension` - audioExtensions/imageExtensions
 * `category` - audioCategories/imageCategories
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
  if (filterParameter !== "") {
    const parameterValues = filterParameter.split(",")
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
  searchType = "image",
  defaultFilters,
}: {
  query: Dictionary<string>
  searchType: SupportedSearchType
  defaultFilters: Partial<Filters>
}) => {
  // The default filterData object from search store doesn't contain provider filters,
  // so we can't use it.
  const filters = deepClone(defaultFilters) as Filters
  const filterTypes = getMediaFilterTypes(searchType)
  const differentFiltersWithSameApiParams = [
    "audioProviders",
    "imageProviders",
    "audioExtensions",
    "imageExtensions",
    "audioCategories",
    "imageCategories",
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
        if (
          queryDataKey === INCLUDE_SENSITIVE_QUERY_PARAM &&
          query[queryDataKey].length > 0
        ) {
          filters[filterDataKey][0].checked = true
        } else {
          const filterValues = query[queryDataKey].split(",")
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
 * Compares two API queries, excluding the search term (`q`) parameter.
 */
export const areQueriesEqual = (
  newQuery: PaginatedSearchQuery,
  oldQuery: PaginatedSearchQuery
): boolean => {
  const queryKeys = (query: PaginatedSearchQuery) =>
    Object.keys(query).filter(
      (k) => k !== "q"
    ) as (keyof PaginatedSearchQuery)[]
  const oldQueryKeys = queryKeys(oldQuery)
  const newQueryKeys = queryKeys(newQuery)
  if (oldQueryKeys.length !== newQueryKeys.length) {
    return false
  }

  for (const key of oldQueryKeys) {
    if (oldQuery[key] !== newQuery[key]) {
      return false
    }
  }
  return true
}

/**
 * The vue-router's query can have values of a string or an array of strings.
 * This function converts the query to a dictionary where the values
 * are always strings. If the parameter has multiple values, the first value
 * is used.
 * * @param queryDictionary - the query param dictionary provided by Vue router
 */
export const queryDictionaryToQueryParams = (
  queryDictionary: Context["query"]
): Dictionary<string> => {
  const queryParams = {} as Dictionary<string>
  Object.keys(queryDictionary).forEach((key) => {
    const value = queryDictionary[key]
    // If the parameter is an array, use the first value.
    const parameter = firstParam(value)
    if (parameter) {
      queryParams[key] = parameter
    }
  })
  return queryParams
}
