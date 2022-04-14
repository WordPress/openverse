import { setActivePinia, createPinia } from 'pinia'

import { nextTick } from '@nuxtjs/composition-api'

import { filterData, mediaFilterKeys } from '~/constants/filters'
import {
  ALL_MEDIA,
  AUDIO,
  IMAGE,
  supportedSearchTypes,
  VIDEO,
} from '~/constants/media'

import { useSearchStore } from '~/stores/search'

describe('Search Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  describe('state', () => {
    it('sets initial filters to filterData', () => {
      const searchStore = useSearchStore()
      expect(searchStore.filters).toEqual(filterData)
    })
  })
  describe('getters', () => {
    /**
     * Check for some special cases:
     * - `mature` and `searchBy`.
     * - several options for single filter.
     * - media specific filters that are unique (durations).
     * - media specific filters that have the same API param (extensions)
     */
    it.each`
      query                                          | searchType   | filterCount
      ${{ licenses: ['by'], mature: ['mature'] }}    | ${IMAGE}     | ${1}
      ${{ licenses: ['by'], searchBy: ['creator'] }} | ${ALL_MEDIA} | ${2}
      ${{ licenses: ['cc0', 'pdm', 'by', 'by-nc'] }} | ${ALL_MEDIA} | ${4}
      ${{ durations: ['medium'] }}                   | ${AUDIO}     | ${1}
      ${{ imageExtensions: ['svg'] }}                | ${IMAGE}     | ${1}
      ${{ audioExtensions: ['mp3'] }}                | ${AUDIO}     | ${1}
    `(
      'returns correct filter status for $query and searchType $searchType',
      ({ query, searchType, filterCount }) => {
        const searchStore = useSearchStore()
        searchStore.setSearchType(searchType)
        for (let [filterType, values] of Object.entries(query)) {
          values.forEach((val) =>
            searchStore.toggleFilter({ filterType, code: val })
          )
        }

        expect(searchStore.appliedFilterCount).toEqual(filterCount)
        expect(searchStore.isAnyFilterApplied).toBe(filterCount > 0)
      }
    )
  })
  describe('getters', () => {
    /**
     * For non-supported search types, the filters fall back to 'All content' filters.
     * Number of displayed filters is one less than the number of mediaFilterKeys
     * because `mature` filter is not displayed.
     */
    it.each`
      searchType   | filterTypeCount
      ${IMAGE}     | ${mediaFilterKeys[IMAGE].length}
      ${AUDIO}     | ${mediaFilterKeys[AUDIO].length}
      ${ALL_MEDIA} | ${mediaFilterKeys[ALL_MEDIA].length}
      ${VIDEO}     | ${mediaFilterKeys[VIDEO].length}
    `(
      'mediaFiltersForDisplay returns $filterTypeCount filters for $searchType',
      ({ searchType, filterTypeCount }) => {
        const searchStore = useSearchStore()
        searchStore.setSearchType(searchType)
        const filtersForDisplay = searchStore.searchFilters
        const expectedFilterCount = Math.max(0, filterTypeCount - 1)
        expect(Object.keys(filtersForDisplay).length).toEqual(
          expectedFilterCount
        )
      }
    )
    /**
     * Check for some special cases:
     * - `mature` and `searchBy`.
     * - several options for single filter.
     * - media specific filters that are unique (durations).
     * - media specific filters that have the same API param (extensions)
     * - no 'q' parameter in the query.
     */
    it.each`
      query                                               | searchType
      ${{ q: 'cat', license: 'by', mature: 'true' }}      | ${IMAGE}
      ${{ license: 'by', mature: 'true' }}                | ${IMAGE}
      ${{ license: '', mature: '' }}                      | ${IMAGE}
      ${{ q: 'cat', license: 'by', searchBy: 'creator' }} | ${ALL_MEDIA}
      ${{ q: 'cat', license: 'pdm,cc0,by,by-nc' }}        | ${ALL_MEDIA}
      ${{ q: 'cat', duration: 'medium' }}                 | ${AUDIO}
      ${{ q: 'cat', extension: 'svg' }}                   | ${IMAGE}
      ${{ q: 'cat', extension: 'svg' }}                   | ${AUDIO}
      ${{ q: 'cat', extension: 'mp3' }}                   | ${AUDIO}
    `(
      'returns correct searchQueryParams and filter status for $query and searchType $searchType',
      ({ query, searchType }) => {
        const searchStore = useSearchStore()
        const expectedQueryParams = query
        // It should discard the values that are not applicable for the search type:
        if (searchType === AUDIO && query.extension === 'svg') {
          delete expectedQueryParams.extension
        }
        searchStore.setSearchStateFromUrl({
          path: `/search/${searchType === ALL_MEDIA ? '' : searchType}`,
          urlQuery: { ...expectedQueryParams },
        })
        // Edge-case: query parameter value is a blank string
        for (let param in expectedQueryParams) {
          if (expectedQueryParams[param] === '')
            delete expectedQueryParams[param]
        }
        // Should add a blank string as `q` value if `q` is not in query
        if (!('q' in expectedQueryParams)) {
          expectedQueryParams.q = ''
        }
        expect(searchStore.searchQueryParams).toEqual(expectedQueryParams)
      }
    )
  })
  describe('actions', () => {
    it.each(['foo', ''])(
      '`setSearchTerm correctly updates the searchTerm',
      (searchTerm) => {
        const searchStore = useSearchStore()
        const expectedSearchTerm = searchTerm
        searchStore.setSearchTerm(searchTerm)
        expect(searchStore.searchTerm).toEqual(expectedSearchTerm)
      }
    )
    it.each(supportedSearchTypes)(
      'setSearchType correctly updates the searchType',
      (type) => {
        const searchStore = useSearchStore()
        searchStore.setSearchType(type)

        expect(searchStore.searchType).toEqual(type)
      }
    )

    // TODO: add support for video path
    it.each`
      searchType | path
      ${'all'}   | ${'/search/'}
      ${'image'} | ${'/search/image/'}
      ${'audio'} | ${'/search/audio/'}
      ${'video'} | ${'/search/video'}
    `(
      "`setSearchStateFromUrl` should set searchType '$searchType' from path '$path'",
      ({ searchType, path }) => {
        const searchStore = useSearchStore()
        searchStore.setSearchStateFromUrl({ path: path, urlQuery: {} })

        expect(searchStore.searchType).toEqual(searchType)
      }
    )

    it.each`
      query                                | path                | searchType
      ${{ license: 'cc0,by', q: 'cat' }}   | ${'/search/'}       | ${ALL_MEDIA}
      ${{ searchBy: 'creator', q: 'dog' }} | ${'/search/image/'} | ${IMAGE}
      ${{ mature: 'true', q: 'galah' }}    | ${'/search/audio/'} | ${AUDIO}
      ${{ duration: 'medium' }}            | ${'/search/image'}  | ${IMAGE}
    `(
      "`setSearchStateFromUrl` should set '$searchType' from query  $query and path '$path'",
      ({ query, path, searchType }) => {
        const searchStore = useSearchStore()
        const expectedQuery = { ...searchStore.searchQueryParams, ...query }
        // The values that are not applicable for the search type should be discarded
        if (searchType === IMAGE) {
          delete expectedQuery.duration
        }

        searchStore.setSearchStateFromUrl({ path: path, urlQuery: query })

        expect(searchStore.searchType).toEqual(searchType)
        expect(searchStore.searchQueryParams).toEqual(expectedQuery)
      }
    )

    it.each`
      filters                                                               | query
      ${[['licenses', 'by'], ['licenses', 'by-nc-sa']]}                     | ${['license', 'by,by-nc-sa']}
      ${[['licenseTypes', 'commercial'], ['licenseTypes', 'modification']]} | ${['license_type', 'commercial,modification']}
      ${[['searchBy', 'creator']]}                                          | ${['searchBy', 'creator']}
      ${[['mature', 'mature']]}                                             | ${['mature', 'true']}
      ${[['sizes', 'large']]}                                               | ${['size', undefined]}
    `(
      'toggleFilter updates the query values to $query',
      ({ filters, query }) => {
        const searchStore = useSearchStore()
        for (const filterItem of filters) {
          const [filterType, code] = filterItem
          searchStore.toggleFilter({ filterType, code })
        }
        expect(searchStore.searchQueryParams[query[0]]).toEqual(query[1])
      }
    )

    it.each([ALL_MEDIA, IMAGE, AUDIO, VIDEO])(
      'Clears filters when search type is %s',
      (searchType) => {
        const searchStore = useSearchStore()
        const expectedQueryParams = { q: 'cat' }
        searchStore.setSearchStateFromUrl({
          path: `/search/${searchType === ALL_MEDIA ? '' : searchType}`,
          urlQuery: {
            q: 'cat',
            license: 'cc0',
            sizes: 'large',
            extension: 'jpg,mp3',
          },
        })
        if (supportedSearchTypes.includes(searchType)) {
          expect(searchStore.query).not.toEqual(expectedQueryParams)
        }
        searchStore.clearFilters()
        expect(searchStore.searchQueryParams).toEqual(expectedQueryParams)
      }
    )
  })
  describe('actions', () => {
    it.each`
      filterType           | codeIdx
      ${'licenses'}        | ${0}
      ${'licenseTypes'}    | ${0}
      ${'imageExtensions'} | ${0}
      ${'imageCategories'} | ${0}
      ${'searchBy'}        | ${0}
      ${'aspectRatios'}    | ${0}
      ${'sizes'}           | ${0}
      ${'mature'}          | ${0}
    `(
      'toggleFilter updates $filterType filter state',
      ({ filterType, codeIdx }) => {
        const searchStore = useSearchStore()

        searchStore.toggleFilter({ filterType, codeIdx })
        const filterItem = searchStore.filters[filterType][codeIdx]
        expect(filterItem.checked).toEqual(true)
      }
    )

    it('toggleFilter updates isFilterApplied with provider', () => {
      const searchStore = useSearchStore()
      searchStore.setSearchType(IMAGE)
      searchStore.initProviderFilters({
        mediaType: IMAGE,
        providers: [{ source_name: 'met', display_name: 'Met' }],
      })

      searchStore.toggleFilter({ filterType: 'imageProviders', code: 'met' })
      expect(searchStore.appliedFilterCount).toEqual(1)
      expect(searchStore.isAnyFilterApplied).toEqual(true)
    })

    it('toggleFilter updates isFilterApplied with license type', () => {
      const searchStore = useSearchStore()
      searchStore.toggleFilter({ filterType: 'licenseTypes', codeIdx: 0 })

      expect(searchStore.isAnyFilterApplied).toEqual(true)
    })

    it('initProviderFilters merges with existing provider filters', () => {
      const searchStore = useSearchStore()
      const existingProviderFilters = [{ code: 'met', checked: true }]

      searchStore.$patch({
        filters: { imageProviders: existingProviderFilters },
      })
      const providers = [
        { source_name: 'met', display_name: 'Metropolitan' },
        { source_name: 'flickr', display_name: 'Flickr' },
      ]

      searchStore.initProviderFilters({
        mediaType: 'image',
        providers: providers,
      })

      expect(searchStore.filters.imageProviders).toEqual([
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ])
    })

    it('clearFilters resets filters to initial state', () => {
      const searchStore = useSearchStore()
      searchStore.toggleFilter({ filterType: 'licenses', code: 'by' })
      searchStore.toggleFilter({ filterType: 'licenses', code: 'by-nc' })
      searchStore.toggleFilter({ filterType: 'licenses', code: 'by-nd' })

      searchStore.clearFilters()
      expect(searchStore.filters).toEqual(filterData)
    })

    it('clearFilters sets providers filters checked to false', () => {
      const searchStore = useSearchStore()
      searchStore.filters.imageProviders = [
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ]

      searchStore.clearFilters()
      const expectedFilters = {
        ...searchStore.filters,
        imageProviders: [
          { code: 'met', name: 'Metropolitan', checked: false },
          { code: 'flickr', name: 'Flickr', checked: false },
        ],
      }
      expect(searchStore.filters).toEqual(expectedFilters)
    })

    it.each`
      filterType           | code              | idx
      ${'licenses'}        | ${'cc0'}          | ${1}
      ${'licenseTypes'}    | ${'modification'} | ${1}
      ${'imageExtensions'} | ${'svg'}          | ${3}
      ${'imageCategories'} | ${'photograph'}   | ${0}
      ${'searchBy'}        | ${'creator'}      | ${0}
      ${'mature'}          | ${'mature'}       | ${-0}
      ${'aspectRatios'}    | ${'tall'}         | ${0}
      ${'sizes'}           | ${'medium'}       | ${1}
    `(
      "toggleFilter should set filter '$code' of type '$filterType",
      ({ filterType, code, idx }) => {
        const searchStore = useSearchStore()
        searchStore.toggleFilter({ filterType: filterType, code: code })

        const filterItem = searchStore.filters[filterType][idx]

        expect(filterItem.checked).toEqual(true)
      }
    )
    it.each`
      item                                                    | dependency                                              | disabled
      ${{ code: 'by-nc', filterType: 'licenses' }}            | ${{ filterType: 'licenseTypes', code: 'commercial' }}   | ${true}
      ${{ code: 'by-nc-nd', filterType: 'licenses' }}         | ${{ filterType: 'licenseTypes', code: 'commercial' }}   | ${true}
      ${{ code: 'by-nc-sa', filterType: 'licenses' }}         | ${{ filterType: 'licenseTypes', code: 'commercial' }}   | ${true}
      ${{ code: 'by-nd', filterType: 'licenses' }}            | ${{ filterType: 'licenseTypes', code: 'modification' }} | ${true}
      ${{ code: 'by-nc-nd', filterType: 'licenses' }}         | ${{ filterType: 'licenseTypes', code: 'modification' }} | ${true}
      ${{ code: 'by-nc', filterType: 'licenses' }}            | ${{ filterType: 'licenseTypes', code: 'modification' }} | ${false}
      ${{ code: 'by-nd', filterType: 'licenses' }}            | ${{ filterType: 'licenseTypes', code: 'commercial' }}   | ${false}
      ${{ code: 'commercial', filterType: 'licenseTypes' }}   | ${{ filterType: 'licenses', code: 'by-nc' }}            | ${true}
      ${{ code: 'commercial', filterType: 'licenseTypes' }}   | ${{ filterType: 'licenses', code: 'by-nc-nd' }}         | ${true}
      ${{ code: 'commercial', filterType: 'licenseTypes' }}   | ${{ filterType: 'licenses', code: 'by-nc-sa' }}         | ${true}
      ${{ code: 'modification', filterType: 'licenseTypes' }} | ${{ filterType: 'licenses', code: 'by-nd' }}            | ${true}
      ${{ code: 'modification', filterType: 'licenseTypes' }} | ${{ filterType: 'licenses', code: 'by-nc-nd' }}         | ${true}
    `(
      'isFilterDisabled for $item.code should return $disabled when $dependency.code is checked',
      ({ item, dependency, disabled }) => {
        const searchStore = useSearchStore()
        searchStore.toggleFilter({
          filterType: dependency.filterType,
          code: dependency.code,
        })
        const isDisabled = searchStore.isFilterDisabled(item, item.filterType)
        expect(isDisabled).toBe(disabled)
      }
    )

    it('toggleFilter without code or codeIdx parameters warns about it', () => {
      const searchStore = useSearchStore()
      const expectedFilters = searchStore.filters

      expect(() =>
        searchStore.toggleFilter({ filterType: 'licenses' })
      ).toThrow(
        'Cannot toggle filter of type licenses. Use code or codeIdx parameter'
      )

      expect(searchStore.filters).toEqual(expectedFilters)
    })

    it.each`
      searchType   | nextSearchType | expectedFilterCount
      ${AUDIO}     | ${IMAGE}       | ${25}
      ${IMAGE}     | ${ALL_MEDIA}   | ${12}
      ${ALL_MEDIA} | ${VIDEO}       | ${12}
      ${VIDEO}     | ${AUDIO}       | ${24}
      ${ALL_MEDIA} | ${IMAGE}       | ${25}
    `(
      'changing searchType clears all but $expectedFilterCount $nextSearchType filters ',
      async ({ searchType, nextSearchType, expectedFilterCount }) => {
        const searchStore = useSearchStore()
        searchStore.setSearchType(searchType)
        // Set all filters to checked
        for (let ft in searchStore.filters) {
          for (let f of searchStore.filters[ft]) {
            searchStore.toggleFilter({ filterType: ft, code: f.code })
          }
        }
        searchStore.setSearchType(nextSearchType)
        await nextTick()

        const checkedFilterCount = Object.keys(searchStore.filters)
          .map(
            (key) => searchStore.filters[key].filter((f) => f.checked).length
          )
          .reduce((partialSum, count) => partialSum + count, 0)
        expect(checkedFilterCount).toEqual(expectedFilterCount)
      }
    )

    it('Does not set filter or count filter as applied, and does not raise error for unsupported search types', () => {
      const searchStore = useSearchStore()
      searchStore.toggleFilter({
        filterType: 'licenseTypes',
        code: 'commercial',
      })
      expect(searchStore.isAnyFilterApplied).toEqual(true)

      searchStore.setSearchType(VIDEO)
      searchStore.toggleFilter({
        filterType: 'licenseTypes',
        code: 'commercial',
      })
      expect(searchStore.isAnyFilterApplied).toEqual(false)
    })
  })
})
