import clonedeep from 'lodash.clonedeep'
import { mediaFilterKeys } from '~/store/search'
import getParameterByName from './get-parameter-by-name'
import { ALL_MEDIA } from '~/constants/media'

const filterPropertyMappings = {
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

const getMediaFilterTypes = (searchType) => [...mediaFilterKeys[searchType]]
// {
//   license: 'cc0,pdm,by,by-sa,by-nc,by-nd,by-nc-sa,by-nc-nd',
//   imageCategories: 'photograph,illustration,digitized_artwork',
//   imageExtension: 'jpg,png',
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
 * @param {import('../store/types').SearchType} searchType
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

/**
 * Extract search type from the url. Returns the last part
 * of the path between `/search/` and query, or `all` by default.
 * `/search/?q=test`: all
 * `/search/image?q=test`: image
 * @param {string} queryString
 * @return {import('../store/types').SearchType}
 */
export const queryStringToSearchType = (queryString) => {
  const searchTypePattern = /\/search\/(image|audio|video)\?*/
  let matchedType = queryString.match(searchTypePattern)
  return matchedType === null ? ALL_MEDIA : matchedType[1]
}

/**
 * `source`, `extensions` and `categories` API parameters correspond
 * to different filters in different media types:
 * `source` - audioProviders/imageProviders
 * `extensions` - audioExtensions/imageExtensions
 * `categories` - audioCategories/imageCategories
 * This function sets only filters that are possible for current
 * media type. E.g., for queryString `search/audio?extensions=ogg`
 * the `audioExtensions.ogg.checked` is set to true,
 * but for `search/images?extensions=ogg`, the extensions query parameter
 * is discarded, because `ogg` is not a valid extension for images.
 * @param filterParameter
 * @param parameterFilters
 * @return {*}
 */
const getMediaTypeApiFilters = (filterParameter, parameterFilters) => {
  if (filterParameter !== '') {
    const parameterValues = filterParameter.split(',')
    parameterValues.forEach((parameter) => {
      let existingParameterIdx = parameterFilters.findIndex(
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
 * converts the browser filter query string into the internal filter store data format
 * @param {object} params
 * @param {object} params.query - browser filter query
 * @param {import('../store/types').SearchType} [params.searchType]
 * @param {object} params.defaultFilters default filters for testing purposes
 */
export const queryToFilterData = ({
  query,
  searchType = 'image',
  defaultFilters,
}) => {
  // The default filterData object from search store doesn't contain provider filters,
  // so we can't use it.
  const filters = clonedeep(defaultFilters)
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
      const parameter = query[filterPropertyMappings[filterDataKey]]
      if (parameter) {
        filters[filterDataKey] = getMediaTypeApiFilters(
          parameter,
          filters[filterDataKey]
        )
      }
    } else if (filterDataKey !== 'mature') {
      const queryDataKey = filterPropertyMappings[filterDataKey]
      if (query[queryDataKey]) {
        const filterValues = query[queryDataKey].split(',')
        filterValues.forEach((val) => {
          const idx = filters[filterDataKey].findIndex((f) => f.code === val)
          if (idx >= 0) {
            filters[filterDataKey][idx].checked = true
          }
        })
      }
    }
  })

  if (query.mature) {
    filters.mature = query.mature.toLowerCase() === 'true'
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

export const areQueriesEqual = (oldQuery, newQuery) => {
  for (let key of Object.keys(oldQuery)) {
    if (oldQuery[key] !== newQuery[key]) {
      return false
    }
  }
  return true
}
