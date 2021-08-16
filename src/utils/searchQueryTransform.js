import clonedeep from 'lodash.clonedeep'
import findIndex from 'lodash.findindex'
import { filterData, mediaSpecificFilters } from '~/store-modules/filter-store'
import getParameterByName from './getParameterByName'
import { ALL_MEDIA } from '~/constants/media'

const filterPropertyMappings = {
  licenses: 'license',
  licenseTypes: 'license_type',
  audioCategories: 'categories',
  categories: 'categories',
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

const getMediaFilterTypes = (searchType) => {
  return searchType === ALL_MEDIA
    ? [...mediaSpecificFilters.all]
    : [...mediaSpecificFilters.all, ...mediaSpecificFilters[searchType]]
}

// {
//   license: 'cc0,pdm,by,by-sa,by-nc,by-nd,by-nc-sa,by-nc-nd',
//   categories: 'photograph,illustration,digitized_artwork',
//   extension: 'jpg,png',
//   aspect_ratio: 'square',
//   size: 'small',
//   source: 'animaldiversity,bio_diversity,brooklynmuseum,CAPL,clevelandmuseum,deviantart'
// }

/**
 * joins all the filters which have the checked property `true`
 * to a string separated by commas.
 * eg: "by,nd-nc,nc-sa"
 * @param {array} filter
 */
const filterToString = (filter) =>
  filter
    .filter((f) => f.checked)
    .map((filterItem) => filterItem.code)
    .join(',')

/**
 * converts the filter store object to the data format accepted by the API,
 * which has slightly different property names
 * @param {object} filters object containing the filter data that comes from the filter store
 * @param {string} searchType
 * @param hideEmpty
 * @todo Refactor all of these 'reduce' calls to just use lodash methods :)
 */
export const filtersToQueryData = (
  filters,
  searchType = ALL_MEDIA,
  hideEmpty = true
) => {
  let queryDataObject = {}
  let mediaFilterTypes = getMediaFilterTypes(searchType)
  mediaFilterTypes = mediaFilterTypes.filter((f) => f !== 'mature')
  mediaFilterTypes.reduce((queryData, filterDataKey) => {
    const queryDataKey = filterPropertyMappings[filterDataKey]
    queryData[queryDataKey] = filterToString(filters[filterDataKey])
    return queryData
  }, queryDataObject)

  queryDataObject.mature = filters.mature

  if (hideEmpty) {
    queryDataObject = Object.entries(queryDataObject).reduce(
      (obj, [key, value]) => {
        if (value) {
          obj[key] = value
        }
        return obj
      },
      {}
    )
  }

  return queryDataObject
}

const parseQueryString = (
  queryString,
  queryStringParamKey,
  filterKey,
  data
) => {
  const queryStringFilters = getParameterByName(
    queryStringParamKey,
    queryString
  ).split(',')
  data[filterKey].forEach((filter) => {
    if (findIndex(queryStringFilters, (f) => f === filter.code) >= 0) {
      filter.checked = true
    }
  })
}

/**
 * Extract search type from the url. Returns the the last part
 * of the path between `/search/` and query, or `all` by default.
 * `/search/?q=test`: all
 * `/search/image?q=test`: image
 * @param {string} queryString
 * @return {('all'|'audio'|'image'|'video')}
 */
export const queryStringToSearchType = (queryString) => {
  const searchTypePattern = /\/search\/(image|audio|video)\?*/
  let matchedType = queryString.match(searchTypePattern)
  return matchedType === null ? ALL_MEDIA : matchedType[1]
}

/**
 * converts the browser filter query string into the internal filter store data format
 * @param {string} queryString browser filter query string
 */
export const queryToFilterData = (queryString) => {
  const filters = clonedeep(filterData)
  Object.keys(filterPropertyMappings).forEach((filterDataKey) => {
    if (['audioProviders', 'imageProviders'].includes(filterDataKey)) {
      const providerParameter = getParameterByName(
        filterPropertyMappings[filterDataKey],
        queryString
      )
      filters[filterDataKey] =
        providerParameter === ''
          ? []
          : providerParameter.split(',').map((provider) => ({
              code: provider,
              checked: true,
            }))
    } else if (filterDataKey !== 'mature') {
      const queryDataKey = filterPropertyMappings[filterDataKey]
      parseQueryString(queryString, queryDataKey, filterDataKey, filters)
    }
  })

  const mature = getParameterByName('mature', queryString)
  if (mature) {
    filters.mature = mature.toLowerCase() === 'true'
  }

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
 * @param {string} queryString
 */
export const queryStringToQueryData = (queryString) => {
  const queryDataObject = {}
  const searchType = queryStringToSearchType(queryString)
  const filterTypes = getMediaFilterTypes(searchType).filter(
    (f) => f !== 'mature'
  )
  filterTypes.forEach((filterDataKey) => {
    const queryDataKey = filterPropertyMappings[filterDataKey]
    queryDataObject[queryDataKey] = getParameterByName(
      queryDataKey,
      queryString
    )
  })
  queryDataObject.q = getParameterByName('q', queryString)
  queryDataObject.mature = getParameterByName('mature', queryString)

  return queryDataObject
}
