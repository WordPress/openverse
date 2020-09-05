import store, { filterData } from '@/store/filter-store'
import { TOGGLE_FILTER } from '@/store/action-types'
import {
  SET_FILTER,
  SET_PROVIDERS_FILTERS,
  CLEAR_FILTERS,
  SET_FILTER_IS_VISIBLE,
} from '@/store/mutation-types'

describe('Filter Store', () => {
  describe('state', () => {
    it('state contains licenses', () => {
      const defaultState = store.state('')

      expect(defaultState.filters.licenses).toEqual(filterData.licenses)
    })

    it('state contains license types', () => {
      const defaultState = store.state('')

      expect(defaultState.filters.licenseTypes).toEqual(filterData.licenseTypes)
    })

    it('state contains image types', () => {
      const defaultState = store.state('')

      expect(defaultState.filters.categories).toEqual(filterData.categories)
    })

    it('state contains extensions', () => {
      const defaultState = store.state('')

      expect(defaultState.filters.extensions).toEqual(filterData.extensions)
    })

    it('state contains empty providers list', () => {
      const defaultState = store.state('')

      expect(defaultState.filters.providers).toEqual([])
    })

    it('state contains search by author', () => {
      const defaultState = store.state('')

      expect(defaultState.filters.searchBy.author).toEqual(
        filterData.searchBy.author
      )
    })

    it('state contains mature', () => {
      const defaultState = store.state('')

      expect(defaultState.filters.mature).toEqual(filterData.mature)
    })

    it('gets query from search params', () => {
      const state = store.state(
        '?q=landscapes&source=met&license=by&license_type=commercial&searchBy=creator'
      )
      expect(
        state.filters.providers.find((x) => x.code === 'met').checked
      ).toBeTruthy()
      expect(
        state.filters.licenses.find((x) => x.code === 'by').checked
      ).toBeTruthy()
      expect(
        state.filters.licenseTypes.find((x) => x.code === 'commercial').checked
      ).toBeTruthy()
      expect(state.filters.searchBy.creator).toBeTruthy()
      expect(state.filters.mature).toBeFalsy()
    })

    it('gets mature from search params', () => {
      const state = store.state('?q=mature=true')
      expect(state.filters.mature).toBeTruthy()
    })

    it('gets mature as false from search params', () => {
      const state = store.state('?q=mature=false')
      expect(state.filters.mature).toBeFalsy()
    })

    it('state has filter visible', () => {
      const defaultState = store.state('')

      expect(defaultState.isFilterVisible).toBeTruthy()
    })

    it('state has isFilterApplied default as false', () => {
      const defaultState = store.state('')

      expect(defaultState.isFilterApplied).toBeFalsy()
    })

    it('isFilterApplied is set to true when provider filter is set', () => {
      const state = store.state(
        '?q=landscapes&source=met&license=by&license_type='
      )
      expect(state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when searchBy filter is set', () => {
      const state = store.state('?q=landscapes&searchBy=creator')
      expect(state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when license type filter is set', () => {
      const state = store.state('?q=landscapes&license_type=commercial')
      expect(state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when license filter is set', () => {
      const state = store.state('?q=landscapes&license=by')
      expect(state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when categories filter is set', () => {
      const state = store.state('?q=landscapes&categories=photograph')
      expect(state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when size filter is set', () => {
      const state = store.state('?q=landscapes&size=large')
      expect(state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied is set to true when aspect ratio filter is set', () => {
      const state = store.state('?q=landscapes&aspect_ratio=tall')
      expect(state.isFilterApplied).toBeTruthy()
    })

    it('isFilterApplied remains false when mature filter is set', () => {
      const state = store.state('?q=landscapes&mature=true')
      expect(state.isFilterApplied).toBeFalsy()
    })

    it('isFilterApplied is set to false when no filter is set', () => {
      const state = store.state('?q=landscapes')
      expect(state.isFilterApplied).toBeFalsy()
    })

    it('isFilterVisible should be false when innerWidth property is undefined', () => {
      window.innerWidth = undefined
      const state = store.state('')
      expect(state.isFilterVisible).toBeFalsy()
    })

    it('isFilterVisible should be true when window width is over 800', () => {
      window.innerWidth = 850
      const state = store.state('')
      expect(state.isFilterVisible).toBeTruthy()
    })

    it('isFilterVisible should be false when window width is less then 800', () => {
      window.innerWidth = 500
      const state = store.state('')
      expect(state.isFilterVisible).toBeFalsy()
    })
  })

  describe('mutations', () => {
    let state = null
    let routePushMock = null
    let mutations = null

    beforeEach(() => {
      state = {
        query: { q: 'foo' },
        ...store.state(''),
      }
      routePushMock = jest.fn()
      mutations = store.mutations(routePushMock)
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
      mutations[SET_FILTER](state, { filterType: 'searchBy' })

      expect(state.filters.searchBy.creator).toBeTruthy()
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

    it('SET_FILTER redirects to current path with query object', () => {
      mutations[SET_FILTER](state, {
        filterType: 'categories',
        codeIdx: 0,
        shouldNavigate: true,
      })

      expect(routePushMock).toHaveBeenCalledWith({
        path: '/',
        query: state.query,
      })
    })

    it('SET_FILTER updates isFilterApplied with provider', () => {
      state.filters.providers = [{ code: 'met', checked: false }]
      mutations[SET_FILTER](state, { filterType: 'providers', codeIdx: 0 })

      expect(state.isFilterApplied).toBeTruthy()
    })

    it('SET_FILTER updates isFilterApplied with license type', () => {
      mutations[SET_FILTER](state, { filterType: 'licenseTypes', codeIdx: 0 })

      expect(state.isFilterApplied).toBeTruthy()
    })

    it('SET_FILTER updates isFilterApplied with searchBy', () => {
      mutations[SET_FILTER](state, { filterType: 'searchBy' })

      expect(state.isFilterApplied).toBeTruthy()
    })

    it('SET_FILTER updates isFilterApplied mature', () => {
      mutations[SET_FILTER](state, { filterType: 'mature' })

      expect(state.isFilterApplied).toBeFalsy()
    })

    it('SET_PROVIDERS_FILTERS merges with existing provider filters', () => {
      const existingProviderFilters = [{ code: 'met', checked: true }]

      const providers = [
        { source_name: 'met', display_name: 'Metropolitan' },
        { source_name: 'flickr', display_name: 'Flickr' },
      ]

      state.filters.providers = existingProviderFilters

      mutations[SET_PROVIDERS_FILTERS](state, { imageProviders: providers })

      expect(state.filters.providers).toEqual([
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ])
    })

    it('CLEAR_FILTERS resets filters to initial state', () => {
      mutations[CLEAR_FILTERS](state, { shouldNavigate: false })

      expect(state.filters).toEqual(store.state('').filters)
    })

    it('CLEAR_FILTERS sets providers filters checked to false', () => {
      state.filters.providers = [
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ]

      mutations[CLEAR_FILTERS](state, { shouldNavigate: false })

      expect(state.filters.providers).toEqual([
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
        ...store.state(''),
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
