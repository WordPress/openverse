import { createPinia, setActivePinia } from 'pinia'

import store from '~/store/search'

import {
  CLEAR_FILTERS,
  SET_SEARCH_STATE_FROM_URL,
  UPDATE_QUERY_FROM_FILTERS,
} from '~/constants/action-types'
import { SET_SEARCH_TYPE, SET_QUERY } from '~/constants/mutation-types'
import { ALL_MEDIA, AUDIO, IMAGE } from '~/constants/media'

import { useFilterStore } from '~/stores/filter'

const initialState = {
  query: {
    aspect_ratio: '',
    categories: '',
    duration: '',
    extension: '',
    license: '',
    license_type: '',
    mature: '',
    q: '',
    searchBy: '',
    size: '',
    source: '',
  },
  searchType: ALL_MEDIA,
}

describe('Search Store', () => {
  describe('state', () => {
    it('initial state is set correctly', () => {
      const defaultState = store.state()
      expect(defaultState).toEqual(initialState)
    })
  })

  describe('mutations', () => {
    let state = null
    let mutations = null

    beforeEach(() => {
      setActivePinia(createPinia())

      state = {
        search: {
          searchType: 'image',
          query: { q: 'foo' },
        },
        ...store.state(),
      }
      mutations = store.mutations
    })

    it('SET_QUERY updates state', () => {
      const params = { query: { q: 'foo' } }
      mutations[SET_QUERY](state, params)

      expect(state.query.q).toBe(params.query.q)
    })

    it('SET_SEARCH_TYPE updates the state', () => {
      state.searchType = IMAGE
      mutations[SET_SEARCH_TYPE](state, { searchType: AUDIO })
      expect(state.searchType).toEqual(AUDIO)
    })
  })

  describe('actions', () => {
    let state = null
    let commitMock = null
    let dispatchMock = null
    let actions = null
    let context = null

    beforeEach(() => {
      commitMock = jest.fn()
      dispatchMock = jest.fn()
      state = store.state()
      actions = store.actions
      context = {
        commit: commitMock,
        dispatch: dispatchMock,
        rootState: {},
        state: state,
      }
    })

    it.each`
      searchType | path
      ${'all'}   | ${'/search/'}
      ${'image'} | ${'/search/image/'}
      ${'audio'} | ${'/search/audio/'}
      ${'video'} | ${'/search/video'}
    `(
      "SET_SEARCH_STATE_FROM_URL should set searchType '$searchType' from path '$path'",
      ({ searchType, path, mediaType }) => {
        actions[SET_SEARCH_STATE_FROM_URL](
          { commit: commitMock, dispatch: dispatchMock, state },
          { path: path, query: {} }
        )
        expect(commitMock).toHaveBeenLastCalledWith(SET_SEARCH_TYPE, {
          searchType,
        })
        expect(dispatchMock).toHaveBeenCalledWith(UPDATE_QUERY_FROM_FILTERS, {
          mediaType: mediaType,
        })
      }
    )

    it.each`
      query                      | path                | searchType
      ${{ license: 'cc0,by' }}   | ${'/search/'}       | ${ALL_MEDIA}
      ${{ searchBy: 'creator' }} | ${'/search/image/'} | ${IMAGE}
      ${{ mature: 'true' }}      | ${'/search/audio/'} | ${AUDIO}
      ${{ durations: 'medium' }} | ${'/search/image'}  | ${IMAGE}
    `(
      "SET_SEARCH_STATE_FROM_URL should set '$searchType' from query '$path'",
      ({ query, path, searchType }) => {
        actions[SET_SEARCH_STATE_FROM_URL](
          { commit: commitMock, dispatch: dispatchMock, state },
          { path: path, query: query }
        )
        expect(dispatchMock).toHaveBeenCalledWith(UPDATE_QUERY_FROM_FILTERS, {})
        expect(context.commit).toHaveBeenLastCalledWith(SET_SEARCH_TYPE, {
          searchType,
        })
      }
    )

    it('CLEAR_FILTERS resets filters to initial state', async () => {
      const filterStore = useFilterStore()
      filterStore.toggleFilter({ filterType: 'licenses', code: 'by' })
      filterStore.toggleFilter({ filterType: 'licenses', code: 'by-nc' })
      filterStore.toggleFilter({ filterType: 'licenses', code: 'by-nd' })
      actions[CLEAR_FILTERS]({
        commit: commitMock,
        dispatch: dispatchMock,
        state,
      })
      expect(dispatchMock).toHaveBeenCalledWith(UPDATE_QUERY_FROM_FILTERS, {
        q: '',
      })
    })
  })
})
