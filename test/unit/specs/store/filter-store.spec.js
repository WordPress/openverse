import { setActivePinia, createPinia } from 'pinia'

import { useFilterStore } from '~/stores/filter'

import { filterData } from '~/constants/filters'
import { ALL_MEDIA, AUDIO, IMAGE, VIDEO } from '~/constants/media'
import { warn } from '~/utils/console'

jest.mock('~/utils/console', () => ({
  warn: jest.fn(),
}))

describe('Filter Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  describe('state', () => {
    it('sets initial filters to filterData', () => {
      const filterStore = useFilterStore()
      expect(filterStore.filters).toEqual(filterData)
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
        const filterStore = useFilterStore()
        filterStore.setSearchType(searchType)
        for (let [filterType, values] of Object.entries(query)) {
          values.forEach((val) =>
            filterStore.toggleFilter({ filterType, code: val })
          )
        }

        expect(filterStore.appliedFilterCount).toEqual(filterCount)
        expect(filterStore.isAnyFilterApplied).toBe(filterCount > 0)
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
        const filterStore = useFilterStore()

        filterStore.toggleFilter({ filterType, codeIdx })
        const filterItem = filterStore.filters[filterType][codeIdx]
        expect(filterItem.checked).toEqual(true)
      }
    )

    it('toggleFilter updates isFilterApplied with provider', () => {
      const filterStore = useFilterStore()
      filterStore.setSearchType(IMAGE)
      filterStore.initProviderFilters({
        mediaType: IMAGE,
        providers: [{ source_name: 'met', display_name: 'Met' }],
      })

      filterStore.toggleFilter({ filterType: 'imageProviders', code: 'met' })
      expect(filterStore.appliedFilterCount).toEqual(1)
      expect(filterStore.isAnyFilterApplied).toEqual(true)
    })

    it('toggleFilter updates isFilterApplied with license type', () => {
      const filterStore = useFilterStore()
      filterStore.toggleFilter({ filterType: 'licenseTypes', codeIdx: 0 })

      expect(filterStore.isAnyFilterApplied).toEqual(true)
    })

    it('initProviderFilters merges with existing provider filters', () => {
      const filterStore = useFilterStore()
      const existingProviderFilters = [{ code: 'met', checked: true }]

      filterStore.$patch({
        filters: { imageProviders: existingProviderFilters },
      })
      const providers = [
        { source_name: 'met', display_name: 'Metropolitan' },
        { source_name: 'flickr', display_name: 'Flickr' },
      ]

      filterStore.initProviderFilters({
        mediaType: 'image',
        providers: providers,
      })

      expect(filterStore.filters.imageProviders).toEqual([
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ])
    })

    it('clearFilters resets filters to initial state', async () => {
      const filterStore = useFilterStore()
      filterStore.filters.licenses = [
        { code: 'by', checked: true },
        { code: 'by-nc', checked: true },
        { code: 'by-nd', checked: true },
      ]
      filterStore.clearFilters()
      expect(filterStore.filters).toEqual(filterData)
    })

    it('clearFilters sets providers filters checked to false', async () => {
      const filterStore = useFilterStore()
      filterStore.filters.imageProviders = [
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ]

      filterStore.clearFilters()
      const expectedFilters = {
        ...filterStore.filters,
        imageProviders: [
          { code: 'met', name: 'Metropolitan', checked: false },
          { code: 'flickr', name: 'Flickr', checked: false },
        ],
      }
      expect(filterStore.filters).toEqual(expectedFilters)
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
        const filterStore = useFilterStore()
        filterStore.toggleFilter({ filterType: filterType, code: code })

        const filterItem = filterStore.filters[filterType][idx]

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
        const filterStore = useFilterStore()
        filterStore.toggleFilter({
          filterType: dependency.filterType,
          code: dependency.code,
        })
        const isDisabled = filterStore.isFilterDisabled(item, item.filterType)
        expect(isDisabled).toBe(disabled)
      }
    )

    it('toggleFilter without code or codeIdx parameters warns about it', () => {
      const filterStore = useFilterStore()
      const expectedFilters = filterStore.filters

      filterStore.toggleFilter({ filterType: 'licenses' })
      expect(warn).toHaveBeenCalledWith(
        'Cannot toggle filter of type licenses. Use code or codeIdx parameter'
      )
      expect(filterStore.filters).toEqual(expectedFilters)
    })

    it.each`
      searchType   | expectedFilterCount
      ${IMAGE}     | ${25}
      ${AUDIO}     | ${21}
      ${VIDEO}     | ${12}
      ${ALL_MEDIA} | ${12}
    `(
      'clearOtherMediaTypeFilters clears all but $expectedFilterCount $searchType filters ',
      ({ searchType, expectedFilterCount }) => {
        const filterStore = useFilterStore()

        // Set all filters to checked
        for (let ft in filterStore.filters) {
          for (let f of filterStore.filters[ft]) {
            filterStore.toggleFilter({ filterType: ft, code: f.code })
          }
        }

        filterStore.clearOtherMediaTypeFilters({ searchType })
        const checkedFilterCount = Object.keys(filterStore.filters)
          .map(
            (key) => filterStore.filters[key].filter((f) => f.checked).length
          )
          .reduce((partialSum, count) => partialSum + count, 0)
        expect(checkedFilterCount).toEqual(expectedFilterCount)
      }
    )

    it.each`
      query                                             | checkedFilters
      ${{ q: 'cat', license: 'by-sa', mature: 'true' }} | ${[['licenses', 'by-sa'], ['mature', 'mature']]}
      ${{ license: 'cc0', extension: 'svg' }}           | ${[['licenses', 'cc0'], ['imageExtensions', 'svg']]}
    `(
      'updateFiltersFromUrl sets correct filters from $query',
      ({ query, checkedFilters }) => {
        const filterStore = useFilterStore()
        filterStore.updateFiltersFromUrl(query, IMAGE)
        for (let [filterType, filterCode] of checkedFilters) {
          const filterItem = filterStore.filters[filterType].find(
            (f) => f.code === filterCode
          )
          expect(filterItem.checked).toEqual(true)
        }
      }
    )
    it('Does not set filter or count filter as applied, and does not raise error for unsupported search types', () => {
      const filterStore = useFilterStore()
      filterStore.toggleFilter({
        filterType: 'licenseTypes',
        code: 'commercial',
      })
      expect(filterStore.isAnyFilterApplied).toEqual(true)

      filterStore.setSearchType(VIDEO)
      filterStore.toggleFilter({
        filterType: 'licenseTypes',
        code: 'commercial',
      })
      expect(filterStore.isAnyFilterApplied).toEqual(false)
    })
  })
})
