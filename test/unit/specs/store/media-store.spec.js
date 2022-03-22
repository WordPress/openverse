import { createPinia, setActivePinia } from 'pinia'

import store, { createActions } from '~/store/media'
import {
  FETCH_END_MEDIA,
  FETCH_MEDIA_ERROR,
  FETCH_START_MEDIA,
  MEDIA_NOT_FOUND,
  RESET_MEDIA,
  SET_MEDIA,
  SET_MEDIA_ITEM,
} from '~/constants/mutation-types'
import {
  FETCH_MEDIA_ITEM,
  FETCH_SINGLE_MEDIA_TYPE,
  HANDLE_MEDIA_ERROR,
  HANDLE_NO_MEDIA,
} from '~/constants/action-types'
import { AUDIO, IMAGE, supportedMediaTypes } from '~/constants/media'

import { useSearchStore } from '~/stores/search'

describe('Media Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      const state = store.state()
      expect(state.results.audio).toEqual({
        count: 0,
        items: {},
        page: undefined,
        pageCount: 0,
      })
      expect(state.results.image).toEqual({
        count: 0,
        items: {},
        page: undefined,
        pageCount: 0,
      })
      expect(state.fetchState.audio).toEqual({
        fetchingError: null,
        isFetching: false,
        isFinished: false,
      })
      expect(state.fetchState.image).toEqual({
        fetchingError: null,
        isFetching: false,
        isFinished: false,
      })
      expect(state.audio).toEqual({})
      expect(state.image).toEqual({})
    })
  })

  describe('mutations', () => {
    let state = null
    const mutations = store.mutations

    beforeEach(() => {
      state = store.state()
    })

    it('FETCH_START_MEDIA updates state', () => {
      mutations[FETCH_START_MEDIA](state, { mediaType: IMAGE })

      expect(state.fetchState.image.isFetching).toBeTruthy()
      expect(state.fetchState.image.fetchingError).toBeFalsy()
    })

    it('FETCH_END_MEDIA updates state', () => {
      mutations[FETCH_END_MEDIA](state, { mediaType: IMAGE })

      expect(state.fetchState.image.isFetching).toBeFalsy()
    })

    it('FETCH_MEDIA_ERROR updates state', () => {
      mutations[FETCH_MEDIA_ERROR](state, {
        mediaType: IMAGE,
        errorMessage: 'error',
      })

      expect(state.fetchState.image.isFetching).toBeFalsy()
      expect(state.fetchState.image.fetchingError).toBeTruthy()
      expect(state.fetchState.image.fetchingError).toBe('error')
    })

    it.each(supportedMediaTypes)(
      'SET_MEDIA_ITEM updates state for ${mediaType}',
      (mediaType) => {
        const params = {
          item: { title: 'Foo', creator: 'bar', tags: [] },
          mediaType,
        }
        mutations[SET_MEDIA_ITEM](state, params)

        expect(state[mediaType]).toEqual(params.item)
      }
    )

    it('SET_MEDIA updates state persisting images', () => {
      const img1 = {
        id: '81e551de-52ab-4852-90eb-bc3973c342a0',
        title: 'Foo',
        creator: 'foo',
        tags: [],
      }
      const img2 = {
        id: '0dea3af1-27a4-4635-bab6-4b9fb76a59f5',
        title: 'Bar',
        creator: 'bar',
        tags: [],
      }
      state.results.image.items = { [img1.id]: img1 }
      const params = {
        media: { [img2.id]: img2 },
        mediaCount: 2,
        page: 2,
        shouldPersistMedia: true,
        mediaType: IMAGE,
      }
      mutations[SET_MEDIA](state, params)

      expect(state.results.image.items).toEqual({
        [img1.id]: img1,
        [img2.id]: img2,
      })
      expect(state.results.image.count).toBe(params.mediaCount)
      expect(state.results.image.page).toBe(params.page)
    })

    it('SET_MEDIA updates state not persisting images', () => {
      const img = { title: 'Foo', creator: 'bar', tags: [] }
      state.results.image.items = ['img1']
      const params = {
        media: [img],
        mediaCount: 2,
        page: 2,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      mutations[SET_MEDIA](state, params)

      expect(state.results.image.items).toEqual([img])
      expect(state.results.image.count).toBe(params.mediaCount)
      expect(state.results.image.page).toBe(params.page)
    })

    it('SET_MEDIA updates state with default count and page', () => {
      const img = { title: 'Foo', creator: 'bar', tags: [] }
      state.results.image.items = ['img1']
      const params = { media: [img], mediaType: IMAGE }
      mutations[SET_MEDIA](state, params)

      expect(state.results.image.count).toBe(0)
      expect(state.results.image.page).toBe(1)
    })

    it('MEDIA_NOT_FOUND throws an error', () => {
      expect(() =>
        mutations[MEDIA_NOT_FOUND](state, { mediaType: AUDIO })
      ).toThrow('Media of type audio not found')
    })

    it('RESET_MEDIA resets the media type state', () => {
      state = {
        results: {
          image: {
            items: [{ id: 'image1' }, { id: 'image2' }],
            page: 2,
            count: 200,
            pageCount: 2,
          },
        },
      }

      mutations[RESET_MEDIA](state, { mediaType: IMAGE })
      expect(state.results.image.items).toStrictEqual({})
      expect(state.results.image.count).toEqual(0)
      expect(state.results.image.page).toBe(undefined)
      expect(state.results.image.pageCount).toEqual(0)
    })
  })

  describe('actions', () => {
    const detailData = { [AUDIO]: 'audioDetails', [IMAGE]: 'imageDetails' }
    const searchResults = {
      results: { foo: { id: 'foo' }, bar: { id: 'bar' }, zeta: { id: 'zeta' } },
      result_count: 22,
      page_count: 2,
    }
    let services = null
    let state
    let context
    let searchStore

    beforeEach(() => {
      setActivePinia(createPinia())
      services = {
        [AUDIO]: {
          search: jest.fn(() => Promise.resolve(searchResults)),
          getMediaDetail: jest.fn(() => Promise.resolve(detailData[AUDIO])),
        },
        [IMAGE]: {
          search: jest.fn(() => Promise.resolve(searchResults)),
          getMediaDetail: jest.fn(() => Promise.resolve(detailData[IMAGE])),
        },
      }
      state = {
        results: {
          image: {
            items: {
              foo: { id: 'foo' },
              bar: { id: 'bar' },
              zeta: { id: 'zeta' },
            },
            page: undefined,
          },
          audio: {
            items: {
              foo: { id: 'foo' },
              bar: { id: 'bar' },
              zeta: { id: 'zeta' },
            },
            page: undefined,
          },
        },
      }

      context = {
        commit: jest.fn(),
        dispatch: jest.fn(),
        state: state,
      }
    })

    it.each(supportedMediaTypes)(
      'FETCH_SINGLE_MEDIA_TYPE (%s) on success',
      async (mediaType) => {
        searchStore = useSearchStore()
        searchStore.setSearchTerm('cat')
        const params = {
          q: 'foo',
          shouldPersistMedia: true,
          mediaType,
        }
        state.results[mediaType].page = 2
        const action = createActions(services)[FETCH_SINGLE_MEDIA_TYPE]
        await action(context, params)
        expect(context.commit).toHaveBeenCalledWith(FETCH_START_MEDIA, {
          mediaType,
        })
        expect(context.commit).toHaveBeenCalledWith(FETCH_END_MEDIA, {
          mediaType,
        })
        params.page = 3
        expect(context.commit).toHaveBeenCalledWith(SET_MEDIA, {
          media: searchResults.results,
          mediaCount: searchResults.result_count,
          shouldPersistMedia: params.shouldPersistMedia,
          page: params.page,
          pageCount: searchResults.page_count,
          mediaType,
        })
        delete params.mediaType
        delete params.shouldPersistMedia
        expect(services[mediaType].search).toHaveBeenCalledWith(params)
      }
    )

    it('FETCH_SINGLE_MEDIA_TYPE dispatches SEND_SEARCH_QUERY_EVENT', async () => {
      const params = { q: 'foo', shouldPersistMedia: false, mediaType: IMAGE }
      const action = createActions(services)[FETCH_SINGLE_MEDIA_TYPE]
      await action(context, params)
    })

    it('does not dispatch SEND_SEARCH_QUERY_EVENT if page param is available', async () => {
      const params = {
        q: 'foo',
        page: 1,
        shouldPersistMedia: false,
      }
      const action = createActions(services)[FETCH_SINGLE_MEDIA_TYPE]
      await action(context, params)
    })

    it('FETCH_SINGLE_MEDIA_TYPE on error', async () => {
      const mediaType = IMAGE
      services[IMAGE] = {
        search: jest.fn(() => Promise.reject('error')),
      }
      const params = {
        q: 'foo',
        page: 1,
        shouldPersistMedia: false,
        mediaType,
      }
      const action = createActions(services)[FETCH_SINGLE_MEDIA_TYPE]
      await action(context, params)
      await expect(services[IMAGE].search).rejects.toEqual('error')

      expect(context.commit).toHaveBeenCalledWith(FETCH_START_MEDIA, {
        mediaType,
      })
      expect(context.dispatch).toHaveBeenCalledWith(HANDLE_MEDIA_ERROR, {
        error: 'error',
        mediaType,
      })
    })

    it('FETCH_SINGLE_MEDIA_TYPE resets images if page is not defined', async () => {
      const mediaType = IMAGE
      const params = {
        q: 'foo',
        page: undefined,
        shouldPersistMedia: false,
        mediaType,
      }
      const action = createActions(services)[FETCH_SINGLE_MEDIA_TYPE]
      await action(context, params)

      expect(context.commit).toHaveBeenCalledWith(FETCH_START_MEDIA, {
        mediaType,
      })
      expect(context.commit).toHaveBeenCalledWith(FETCH_END_MEDIA, {
        mediaType,
      })
    })

    it('FETCH_SINGLE_MEDIA_TYPE does not reset images if page is defined', async () => {
      const mediaType = IMAGE
      const params = {
        q: 'foo',
        page: 1,
        shouldPersistMedia: false,
        mediaType,
      }
      const action = createActions(services)[FETCH_SINGLE_MEDIA_TYPE]
      await action(context, params)

      expect(context.commit).not.toHaveBeenCalledWith(RESET_MEDIA, {
        mediaType,
      })
    })

    it.each(supportedMediaTypes)(
      'FETCH_MEDIA_ITEM (%s) on success',
      async (mediaType) => {
        const params = { id: 'foo', mediaType }
        const action = createActions(services)[FETCH_MEDIA_ITEM]
        await action(context, params)
        expect(context.commit).toHaveBeenCalledWith(SET_MEDIA_ITEM, {
          item: detailData[mediaType],
          mediaType,
        })
        expect(services[mediaType].getMediaDetail).toHaveBeenCalledWith(params)
      }
    )

    it.each(supportedMediaTypes)(
      'FETCH_MEDIA_ITEM dispatches SEND_RESULT_CLICKED_EVENT',
      (mediaType) => {
        const params = { id: 'foo', mediaType }
        searchStore = useSearchStore()
        searchStore.setSearchTerm('cat')
        const action = createActions(services)[FETCH_MEDIA_ITEM]
        action(context, params)
      }
    )

    it.each(supportedMediaTypes)(
      'FETCH_MEDIA_ITEM on error',
      async (mediaType) => {
        services[mediaType] = {
          getMediaDetail: jest.fn(() => Promise.reject('error')),
        }
        const params = { id: 'foo', mediaType }
        const action = createActions(services)[FETCH_MEDIA_ITEM]
        await action(context, params)
        await expect(services[mediaType].getMediaDetail).rejects.toEqual(
          'error'
        )

        expect(context.dispatch).toHaveBeenLastCalledWith(HANDLE_MEDIA_ERROR, {
          error: 'error',
          mediaType,
        })
      }
    )

    it.each(supportedMediaTypes)(
      'FETCH_MEDIA_ITEM on 404 doesnt break and commits MEDIA_NOT_FOUND',
      async (mediaType) => {
        services[mediaType] = {
          getMediaDetail: jest.fn(() =>
            Promise.reject({ response: { status: 404 } })
          ),
        }
        const params = { id: 'foo', mediaType }
        const action = createActions(services)[FETCH_MEDIA_ITEM]
        await action(context, params)
        expect(context.commit).toHaveBeenCalledWith(MEDIA_NOT_FOUND, {
          mediaType,
        })
      }
    )

    it('HANDLE_MEDIA_ERROR handles 500 error', () => {
      const action = createActions(services)[HANDLE_MEDIA_ERROR]
      const error = { response: { status: 500, message: 'Server error' } }

      action(context, { mediaType: AUDIO, error })
      expect(context.commit).toHaveBeenCalledWith(FETCH_MEDIA_ERROR, {
        errorMessage: 'There was a problem with our servers',
        mediaType: AUDIO,
      })
    })

    it('HANDLE_MEDIA_ERROR handles a 403 error', () => {
      const action = createActions(services)[HANDLE_MEDIA_ERROR]
      const error = { response: { status: 403, message: 'Server error' } }

      action(context, { mediaType: AUDIO, error })
      expect(context.commit).toHaveBeenCalledWith(FETCH_MEDIA_ERROR, {
        errorMessage: error.response.message,
        mediaType: AUDIO,
      })
    })

    it('HANDLE_MEDIA_ERROR throws a new error on error when server did not respond', async () => {
      const action = createActions(services)[HANDLE_MEDIA_ERROR]
      const error = new Error('Server did not respond')
      await expect(
        action(context, { mediaType: AUDIO, error })
      ).rejects.toThrow(error.message)
    })

    it('HANDLE_NO_MEDIA throws an error when media count is 0', async () => {
      const action = createActions(services)[HANDLE_NO_MEDIA]
      await action(context, { mediaCount: 0, mediaType: IMAGE })
      expect(context.commit).toHaveBeenLastCalledWith(FETCH_MEDIA_ERROR, {
        mediaType: IMAGE,
        errorMessage: 'No image found for this query',
      })
    })

    it('HANDLE_NO_MEDIA does not throw an error when media count is not 0', () => {
      const action = createActions(services)[HANDLE_NO_MEDIA]
      action(context, { mediaCount: 1, mediaType: IMAGE })
      expect(context.commit.mock.calls.length).toEqual(0)
    })
  })
})
