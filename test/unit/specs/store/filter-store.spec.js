import store, { filterData } from '~/store-modules/filter-store'
import { TOGGLE_FILTER } from '~/store-modules/action-types'
import {
  SET_FILTER,
  SET_PROVIDERS_FILTERS,
  CLEAR_FILTERS,
  SET_FILTER_IS_VISIBLE,
} from '~/store-modules/mutation-types'

describe('Filter Store', () => {
  describe('state', () => {
    it('state contains licenses', () => {
      expect(store.state.filters.licenses).toEqual(filterData.licenses)
    })

    it('state contains license types', () => {
      expect(store.state.filters.licenseTypes).toEqual(filterData.licenseTypes)
    })

    it('state contains image types', () => {
      expect(store.state.filters.categories).toEqual(filterData.categories)
    })

    it('state contains extensions', () => {
      expect(store.state.filters.extensions).toEqual(filterData.extensions)
    })

    it('state contains empty providers list', () => {
      expect(store.state.filters.providers).toEqual([])
    })

    it('state contains search by author', () => {
      expect(store.state.filters.searchBy.author).toEqual(
        filterData.searchBy.author
      )
    })

    it('state contains mature', () => {
      expect(store.state.filters.mature).toEqual(filterData.mature)
    })

    it('gets query from search params', () => {
      expect(
        store.state.filters.providers.find((x) => x.code === 'met').checked
      ).toBeTruthy()

      expect(
        store.state.filters.licenses.find((x) => x.code === 'by').checked
      ).toBeTruthy()
      expect(
        store.state.filters.licenseTypes.find((x) => x.code === 'commercial')
          .checked
      ).toBeTruthy()

      expect(store.state.filters.searchBy.creator).toBeTruthy()
      expect(store.state.filters.mature).toBeFalsy()
    })

    it('gets mature from search params', () => {
      expect(store.state.filters.mature).toBeTruthy()
    })

    it('gets mature as false from search params', () => {
      expect(store.state.filters.mature).toBeFalsy()
    })

    it('state has filter visible', () => {
      expect(store.state.isFilterVisible).toBeTruthy()
    })

    it('state has isFilterApplied default as false', () => {
      expect(store.state.isFilterApplied).toBeFalsy()
    })

    it('isFilterApplied is set to true when provider filter is set', () => {
      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when searchBy filter is set', () => {
      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when license type filter is set', () => {
      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when license filter is set', () => {
      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when categories filter is set', () => {
      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when size filter is set', () => {
      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when aspect ratio filter is set', () => {
      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied remains false when mature filter is set', () => {
      expect(store.state.isFilterApplied).toBeFalsy()
    })

    it('isFilterApplied is set to false when no filter is set', () => {
      expect(store.state.isFilterApplied).toBeFalsy()
    })

    it('isFilterVisible should be false when innerWidth property is undefined', () => {
      window.innerWidth = undefined
      expect(store.state.isFilterVisible).toBeFalsy()
    })

    it('isFilterVisible should be true when window width is over 800', () => {
      window.innerWidth = 850
      expect(store.state.isFilterVisible).toBeTruthy()
    })

    it('isFilterVisible should be false when window width is less then 800', () => {
      window.innerWidth = 500
      expect(store.state.isFilterVisible).toBeFalsy()
    })
  })

  describe('mutations', () => {
    let state = null
    let mutations = null

    beforeEach(() => {
      state = {
        query: { q: 'foo' },
        ...store.state,
      }
      mutations = store.mutations
    })

    it('SET_FILTER updates license state', () => {
      mutations[SET_FILTER](state, { filterType: 'licenses', codeIdx: 0 })

      expect(store.state.filters.licenses[0].checked).toBeTruthy()
      expect(store.state.query).toEqual(
        expect.objectContaining({ license: state.filters.licenses[0].code })
      )
    })

    it('SET_FILTER updates license type state', () => {
      mutations[SET_FILTER](state, { filterType: 'licenseTypes', codeIdx: 0 })

      expect(store.state.filters.licenseTypes[0].checked).toBeTruthy()
      expect(store.state.query).toEqual(
        expect.objectContaining({
          license_type: state.filters.licenseTypes[0].code,
        })
      )
    })

    it('SET_FILTER updates extensions state', () => {
      mutations[SET_FILTER](state, { filterType: 'extensions', codeIdx: 0 })

      expect(store.state.filters.extensions[0].checked).toBeTruthy()
      expect(store.state.query).toEqual(
        expect.objectContaining({ extension: state.filters.extensions[0].code })
      )
    })

    it('SET_FILTER updates image types state', () => {
      mutations[SET_FILTER](state, { filterType: 'categories', codeIdx: 0 })

      expect(store.state.filters.categories[0].checked).toBeTruthy()
      expect(store.state.query).toEqual(
        expect.objectContaining({
          categories: state.filters.categories[0].code,
        })
      )
    })

    it('SET_FILTER updates search by creator', () => {
      mutations[SET_FILTER](state, { filterType: 'searchBy' })

      expect(store.state.filters.searchBy.creator).toBeTruthy()
      expect(store.state.query).toEqual(
        expect.objectContaining({ searchBy: 'creator' })
      )
    })

    it('SET_FILTER updates mature', () => {
      mutations[SET_FILTER](state, { filterType: 'mature' })

      expect(store.state.filters.mature).toBeTruthy()
      expect(store.state.query).toEqual(
        expect.objectContaining({ mature: true })
      )
    })

    it('SET_FILTER toggles mature', () => {
      state.filters.mature = true
      mutations[SET_FILTER](state, { filterType: 'mature' })

      expect(store.state.filters.mature).toBeFalsy()
    })

    it('SET_FILTER updates aspect ratio', () => {
      mutations[SET_FILTER](state, { filterType: 'aspectRatios', codeIdx: 0 })

      expect(store.state.filters.aspectRatios[0].checked).toBeTruthy()
      expect(store.state.query).toEqual(
        expect.objectContaining({
          aspect_ratio: state.filters.aspectRatios[0].code,
        })
      )
    })

    it('SET_FILTER updates size', () => {
      mutations[SET_FILTER](state, { filterType: 'sizes', codeIdx: 0 })

      expect(store.state.filters.sizes[0].checked).toBeTruthy()
      expect(store.state.query).toEqual(
        expect.objectContaining({ size: state.filters.sizes[0].code })
      )
    })

    it('SET_FILTER updates isFilterApplied with provider', () => {
      state.filters.providers = [{ code: 'met', checked: false }]
      mutations[SET_FILTER](state, { filterType: 'providers', codeIdx: 0 })

      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('SET_FILTER updates isFilterApplied with license type', () => {
      mutations[SET_FILTER](state, { filterType: 'licenseTypes', codeIdx: 0 })

      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('SET_FILTER updates isFilterApplied with searchBy', () => {
      mutations[SET_FILTER](state, { filterType: 'searchBy' })

      expect(store.state.isFilterApplied).toBeTruthy()
    })

    it('SET_FILTER updates isFilterApplied mature', () => {
      mutations[SET_FILTER](state, { filterType: 'mature' })

      expect(store.state.isFilterApplied).toBeFalsy()
    })

    it('SET_PROVIDERS_FILTERS merges with existing provider filters', () => {
      const existingProviderFilters = [{ code: 'met', checked: true }]

      const providers = [
        { source_name: 'met', display_name: 'Metropolitan' },
        { source_name: 'flickr', display_name: 'Flickr' },
      ]

      state.filters.providers = existingProviderFilters

      mutations[SET_PROVIDERS_FILTERS](state, { imageProviders: providers })

      expect(store.state.filters.providers).toEqual([
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ])
    })

    it('CLEAR_FILTERS resets filters to initial state', () => {
      mutations[CLEAR_FILTERS](state, { shouldNavigate: false })
    })

    it('CLEAR_FILTERS sets providers filters checked to false', () => {
      state.filters.providers = [
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ]

      mutations[CLEAR_FILTERS](state, { shouldNavigate: false })

      expect(store.state.filters.providers).toEqual([
        { code: 'met', name: 'Metropolitan', checked: false },
        { code: 'flickr', name: 'Flickr', checked: false },
      ])
    })

    it('SET_FILTER_IS_VISIBLE updates state', () => {
      const params = { isFilterVisible: 'bar' }
      mutations[SET_FILTER_IS_VISIBLE](state, params)

      expect(store.state.isFilterVisible).toBe(params.isFilterVisible)
    })
  })

  describe('actions', () => {
    let state = null
    let commitMock = null
    let dispatchMock = null
    let actions = null

    beforeEach(() => {
      state = {
        query: { q: 'foo' },
        ...store.state,
      }
      commitMock = jest.fn()
      dispatchMock = jest.fn()
      actions = store.actions
    })

    it('TOGGLE_FILTER commits SET_FILTER with filter index', () => {
      state.filters.providers = [
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ]

      const params = { filterType: 'providers', code: 'flickr' }

      actions[TOGGLE_FILTER](
        { commit: commitMock, dispatch: dispatchMock, state },
        params
      )

      expect(commitMock).toHaveBeenCalledWith(SET_FILTER, {
        codeIdx: 1,
        ...params,
      })
    })
  })
})
