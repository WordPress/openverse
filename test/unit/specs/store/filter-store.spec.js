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
      const defaultState = store.state

      expect(defaultState.filters.licenses).toEqual(filterData.licenses)
    })

    it('state contains license types', () => {
      const defaultState = store.state

      expect(defaultState.filters.licenseTypes).toEqual(filterData.licenseTypes)
    })

    it('state contains image types', () => {
      const defaultState = store.state

      expect(defaultState.filters.categories).toEqual(filterData.categories)
    })

    it('state contains extensions', () => {
      const defaultState = store.state

      expect(defaultState.filters.extensions).toEqual(filterData.extensions)
    })

    it('state contains empty providers list', () => {
      const defaultState = store.state

      expect(defaultState.filters.imageProviders).toEqual([])
    })

    it('state contains search by author', () => {
      const defaultState = store.state

      expect(defaultState.filters.searchBy.author).toEqual(
        filterData.searchBy.author
      )
    })

    it('state contains mature', () => {
      const defaultState = store.state

      expect(defaultState.filters.mature).toEqual(filterData.mature)
    })

    it('state has filter hidden', () => {
      const defaultState = store.state

      expect(defaultState.isFilterVisible).toBeFalsy()
    })

    it('isFilterVisible should be false when innerWidth property is undefined', () => {
      window.innerWidth = undefined
      const state = store.state
      expect(state.isFilterVisible).toBeFalsy()
    })
    it('isFilterVisible should be false when window width is less then 800', () => {
      window.innerWidth = 500
      const state = store.state
      expect(state.isFilterVisible).toBeFalsy()
    })
  })

  describe('mutations', () => {
    let state = null
    let mutations = null
    let getters = null

    beforeEach(() => {
      state = {
        searchType: 'image',
        query: { q: 'foo' },
        ...store.state,
      }
      mutations = store.mutations
      getters = store.getters
    })

    it('SET_FILTER updates license state', () => {
      mutations[SET_FILTER](state, { filterType: 'licenses', codeIdx: 0 })

      expect(state.filters.licenses[0].checked).toBeTruthy()
      expect(state.query).toEqual(
        expect.objectContaining({ license: state.filters.licenses[0].code })
      )
    })

    it('SET_FILTER updates license type state', () => {
      mutations[SET_FILTER](state, { filterType: 'licenseTypes', codeIdx: 0 })

      expect(state.filters.licenseTypes[0].checked).toBeTruthy()
      expect(state.query).toEqual(
        expect.objectContaining({
          license_type: state.filters.licenseTypes[0].code,
        })
      )
    })

    it('SET_FILTER updates extensions state', () => {
      mutations[SET_FILTER](state, { filterType: 'extensions', codeIdx: 0 })

      expect(state.filters.extensions[0].checked).toBeTruthy()
      expect(state.query).toEqual(
        expect.objectContaining({ extension: state.filters.extensions[0].code })
      )
    })

    it('SET_FILTER updates image types state', () => {
      mutations[SET_FILTER](state, { filterType: 'categories', codeIdx: 0 })

      expect(state.filters.categories[0].checked).toBeTruthy()
      expect(state.query).toEqual(
        expect.objectContaining({
          categories: state.filters.categories[0].code,
        })
      )
    })

    it('SET_FILTER updates search by creator', () => {
      mutations[SET_FILTER](state, { filterType: 'searchBy', codeIdx: 0 })

      expect(state.filters.searchBy[0].checked).toBeTruthy()
      expect(state.query).toEqual(
        expect.objectContaining({ searchBy: 'creator' })
      )
    })

    it('SET_FILTER updates mature', () => {
      mutations[SET_FILTER](state, { filterType: 'mature' })

      expect(state.filters.mature).toBeTruthy()
      expect(state.query).toEqual(expect.objectContaining({ mature: true }))
    })

    it('SET_FILTER toggles mature', () => {
      state.filters.mature = true
      mutations[SET_FILTER](state, { filterType: 'mature' })

      expect(state.filters.mature).toBeFalsy()
    })

    it('SET_FILTER updates aspect ratio', () => {
      mutations[SET_FILTER](state, { filterType: 'aspectRatios', codeIdx: 0 })

      expect(state.filters.aspectRatios[0].checked).toBeTruthy()
      expect(state.query).toEqual(
        expect.objectContaining({
          aspect_ratio: state.filters.aspectRatios[0].code,
        })
      )
    })

    it('SET_FILTER updates size', () => {
      mutations[SET_FILTER](state, { filterType: 'sizes', codeIdx: 0 })

      expect(state.filters.sizes[0].checked).toBeTruthy()
      expect(state.query).toEqual(
        expect.objectContaining({ size: state.filters.sizes[0].code })
      )
    })

    it('SET_FILTER updates isFilterApplied with provider', () => {
      state.filters.imageProviders = [{ code: 'met', checked: false }]
      mutations[SET_FILTER](state, { filterType: 'imageProviders', codeIdx: 0 })

      expect(getters.isAnyFilterApplied).toBeTruthy()
    })

    it('SET_FILTER updates isFilterApplied with license type', () => {
      mutations[SET_FILTER](state, { filterType: 'licenseTypes', codeIdx: 0 })

      expect(getters.isAnyFilterApplied).toBeTruthy()
    })

    it('SET_FILTER updates mature', () => {
      mutations[SET_FILTER](state, { filterType: 'mature' })

      expect(state.filters.mature).toBeTruthy()
    })

    it('SET_PROVIDERS_FILTERS merges with existing provider filters', () => {
      const existingProviderFilters = [{ code: 'met', checked: true }]

      const providers = [
        { source_name: 'met', display_name: 'Metropolitan' },
        { source_name: 'flickr', display_name: 'Flickr' },
      ]

      state.filters.imageProviders = existingProviderFilters

      mutations[SET_PROVIDERS_FILTERS](state, {
        mediaType: 'image',
        providers: providers,
      })

      expect(state.filters.imageProviders).toEqual([
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ])
    })

    it('CLEAR_FILTERS resets filters to initial state', async () => {
      mutations[CLEAR_FILTERS]({
        query: { q: 'foo' },
        ...store.state,
      })
      expect(state.filters).toEqual(filterData)
    })

    it('CLEAR_FILTERS sets providers filters checked to false', async () => {
      state.filters.imageProviders = [
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ]

      mutations[CLEAR_FILTERS](state)
      expect(state.filters.imageProviders).toEqual([
        { code: 'met', name: 'Metropolitan', checked: false },
        { code: 'flickr', name: 'Flickr', checked: false },
      ])
    })

    it('SET_FILTER_IS_VISIBLE updates state', () => {
      const params = { isFilterVisible: 'bar' }
      mutations[SET_FILTER_IS_VISIBLE](state, params)

      expect(state.isFilterVisible).toBe(params.isFilterVisible)
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
