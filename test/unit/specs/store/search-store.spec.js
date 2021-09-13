import store from '~/store-modules/search-store'
import {
  SET_IMAGE,
  SET_IMAGE_PAGE,
  SET_MEDIA,
  SET_QUERY,
  MEDIA_NOT_FOUND,
  FETCH_START_MEDIA,
  FETCH_END_MEDIA,
  FETCH_MEDIA_ERROR,
} from '~/store-modules/mutation-types'
import {
  FETCH_IMAGE,
  FETCH_COLLECTION_IMAGES,
  FETCH_MEDIA,
} from '~/store-modules/action-types'
import { IMAGE } from '~/constants/media'

describe('Search Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      const state = store.state
      expect(state.imagesCount).toBe(0)
      expect(state.imagePage).toBe(1)
      expect(state.images).toHaveLength(0)
      expect(state.isFetching.images).toBeFalsy()
      expect(state.isFetchingError.images).toBeTruthy()
      expect(state.query.q).toBe(undefined)
      expect(state.errorMessage).toBe(null)
    })
  })

  describe('mutations', () => {
    let state = null
    const mutations = store.mutations

    beforeEach(() => {
      state = {
        isFetching: {},
        isFetchingError: {},
        count: {},
      }
    })

    it('FETCH_START_MEDIA updates state', () => {
      mutations[FETCH_START_MEDIA](state, { mediaType: IMAGE })

      expect(state.isFetching.images).toBeTruthy()
      expect(state.isFetchingError.images).toBeFalsy()
    })

    it('FETCH_END_MEDIA updates state', () => {
      mutations[FETCH_END_MEDIA](state, { mediaType: IMAGE })

      expect(state.isFetching.images).toBeFalsy()
    })

    it('FETCH_MEDIA_ERROR updates state', () => {
      mutations[FETCH_MEDIA_ERROR](state, {
        mediaType: IMAGE,
        errorMessage: 'error',
      })

      expect(state.isFetching.images).toBeFalsy()
      expect(state.isFetchingError.images).toBeTruthy()
      expect(state.errorMessage).toBe('error')
    })

    it('SET_IMAGE updates state', () => {
      const params = { image: { title: 'Foo', creator: 'bar', tags: [] } }
      mutations[SET_IMAGE](state, params)

      expect(state.image).toEqual(params.image)
    })

    it('SET_IMAGE_PAGE updates state', () => {
      const params = { imagePage: 1 }
      mutations[SET_IMAGE_PAGE](state, params)

      expect(state.imagePage).toBe(params.imagePage)
    })

    it('SET_MEDIA updates state persisting images', () => {
      const img1 = { title: 'Foo', creator: 'foo', tags: [] }
      const img2 = { title: 'Bar', creator: 'bar', tags: [] }
      state.images = [img1]
      const params = {
        media: [img2],
        mediaCount: 2,
        page: 2,
        shouldPersistMedia: true,
        mediaType: IMAGE,
      }
      mutations[SET_MEDIA](state, params)

      expect(state.images).toEqual([img1, img2])
      expect(state.count.images).toBe(params.mediaCount)
      expect(state.imagePage).toBe(params.page)
    })

    it('SET_MEDIA updates state not persisting images', () => {
      const img = { title: 'Foo', creator: 'bar', tags: [] }
      state.images = ['img1']
      const params = {
        media: [img],
        mediaCount: 2,
        page: 2,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      mutations[SET_MEDIA](state, params)

      expect(state.images).toEqual([img])
      expect(state.count.images).toBe(params.mediaCount)
      expect(state.imagePage).toBe(params.page)
    })

    it('SET_MEDIA updates state with default count and page', () => {
      const img = { title: 'Foo', creator: 'bar', tags: [] }
      state.images = ['img1']
      const params = { media: [img], mediaType: IMAGE }
      mutations[SET_MEDIA](state, params)

      expect(state.count.images).toBe(0)
      expect(state.imagePage).toBe(1)
    })

    it('SET_QUERY updates state', () => {
      const params = { query: { q: 'foo' } }
      mutations[SET_QUERY](state, params)

      expect(state.query.q).toBe(params.query.q)
    })

    it('SET_QUERY resets images to empty array', () => {
      const params = { query: { q: 'bar' } }
      state.query = {
        q: 'foo',
        images: [{ id: 'foo' }],
      }
      mutations[SET_QUERY](state, params)

      expect(state.query.q).toBe('bar')
      expect(state.images).toEqual([])
    })
  })

  describe('actions', () => {
    const searchData = { results: ['foo'], result_count: 1 }
    const imageDetailData = 'imageDetails'
    let audioServiceMock = null
    let imageServiceMock = null
    let commit = null
    let dispatch = null
    let state = {}

    beforeEach(() => {
      imageServiceMock = {
        search: jest.fn(() => Promise.resolve({ data: searchData })),
        getProviderCollection: jest.fn(() =>
          Promise.resolve({ data: searchData })
        ),
        getMediaDetail: jest.fn(() =>
          Promise.resolve({ data: imageDetailData })
        ),
      }
      audioServiceMock = {
        search: jest.fn(() => Promise.resolve({ data: searchData })),
        getProviderCollection: jest.fn(() =>
          Promise.resolve({ data: searchData })
        ),
        getMediaDetail: jest.fn(() =>
          Promise.resolve({ data: imageDetailData })
        ),
      }
      commit = jest.fn()
      dispatch = jest.fn()
      state = {
        usageSessionId: 'foo session id',
        images: [{ id: 'foo' }, { id: 'bar' }, { id: 'zeta' }],
        query: { q: 'foo query' },
      }
    })

    it('FETCH_MEDIA on success', (done) => {
      const params = {
        q: 'foo',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_MEDIA
      ]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(commit).toBeCalledWith(FETCH_END_MEDIA, { mediaType: IMAGE })

        expect(commit).toBeCalledWith(SET_MEDIA, {
          media: searchData.results,
          mediaCount: searchData.result_count,
          shouldPersistMedia: params.shouldPersistMedia,
          page: params.page,
          mediaType: IMAGE,
        })

        expect(imageServiceMock.search).toBeCalledWith(params)

        done()
      })
    })

    it('FETCH_MEDIA dispatches SEND_SEARCH_QUERY_EVENT', () => {
      const params = { q: 'foo', shouldPersistMedia: false, mediaType: IMAGE }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_MEDIA
      ]
      action({ commit, dispatch, state }, params)

      expect(dispatch).toHaveBeenLastCalledWith('SEND_SEARCH_QUERY_EVENT', {
        query: params.q,
        sessionId: state.usageSessionId,
      })
    })

    it('does not dispatch SEND_SEARCH_QUERY_EVENT if page param is available', () => {
      const params = {
        q: 'foo',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_MEDIA
      ]
      action({ commit, dispatch, state }, params)

      expect(dispatch).not.toHaveBeenLastCalledWith('SEND_SEARCH_QUERY_EVENT', {
        query: params.q,
        sessionId: state.usageSessionId,
      })
    })

    it('FETCH_COLLECTION_IMAGES on success', (done) => {
      const params = {
        provider: 'met',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_COLLECTION_IMAGES
      ]
      action({ commit, dispatch }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(commit).toBeCalledWith(FETCH_END_MEDIA, { mediaType: IMAGE })

        expect(commit).toBeCalledWith(SET_MEDIA, {
          media: searchData.results,
          mediaCount: searchData.result_count,
          shouldPersistMedia: params.shouldPersistMedia,
          page: params.page,
          mediaType: IMAGE,
        })

        const newParams = { ...params, source: params.provider }
        delete newParams.provider
        expect(imageServiceMock.getProviderCollection).toBeCalledWith(newParams)
        done()
      })
    })

    it('FETCH_COLLECTION_IMAGES calls search API if q param exist', (done) => {
      const params = {
        q: 'nature',
        provider: 'met',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_COLLECTION_IMAGES
      ]
      action({ commit, dispatch }, params).then(() => {
        const newParams = { ...params, source: params.provider }
        delete newParams.provider
        expect(imageServiceMock.search).toBeCalledWith(newParams)

        done()
      })
    })

    it('FETCH_COLLECTION_IMAGES calls getProviderCollection API if li param exist', (done) => {
      const params = {
        li: 'by',
        provider: 'met',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_COLLECTION_IMAGES
      ]
      action({ commit, dispatch }, params).then(() => {
        const newParams = { ...params, source: params.provider }
        delete newParams.provider
        expect(imageServiceMock.getProviderCollection).toBeCalledWith(newParams)

        done()
      })
    })

    it('FETCH_COLLECTION_IMAGES calls getProviderCollection API if lt param exist', (done) => {
      const params = {
        lt: 'commercial',
        provider: 'met',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_COLLECTION_IMAGES
      ]
      action({ commit, dispatch }, params).then(() => {
        const newParams = { ...params, source: params.provider }
        delete newParams.provider
        expect(imageServiceMock.getProviderCollection).toBeCalledWith(newParams)

        done()
      })
    })

    it('FETCH_COLLECTION_IMAGES calls search API if q param exist', (done) => {
      const params = {
        q: 'nature',
        provider: 'met',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_COLLECTION_IMAGES
      ]
      action({ commit, dispatch }, params).then(() => {
        const newParams = { ...params, source: params.provider }
        delete newParams.provider
        expect(imageServiceMock.search).toBeCalledWith(newParams)

        done()
      })
    })

    it('FETCH_MEDIA on error', (done) => {
      const failedMock = {
        search: jest.fn(() => Promise.reject('error')),
      }
      const params = {
        q: 'foo',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(failedMock, failedMock)[FETCH_MEDIA]
      action({ commit, dispatch, state }, params).catch((error) => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(dispatch).toBeCalledWith('HANDLE_IMAGE_ERROR', error)
      })
      done()
    })

    it('FETCH_COLLECTION_IMAGES on error', (done) => {
      const failedMock = {
        getProviderCollection: jest.fn(() => Promise.reject('error')),
        search: jest.fn(() => Promise.reject('error')),
      }
      const params = {
        q: 'foo',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(failedMock, failedMock)[
        FETCH_COLLECTION_IMAGES
      ]
      action({ commit, dispatch }, params).catch((error) => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(dispatch).toBeCalledWith('HANDLE_IMAGE_ERROR', error)
      })
      done()
    })

    it('FETCH_MEDIA resets images if page is not defined', (done) => {
      const params = {
        q: 'foo',
        page: undefined,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_MEDIA
      ]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, {
          mediaType: IMAGE,
        })

        expect(commit).toBeCalledWith(FETCH_END_MEDIA, {
          mediaType: IMAGE,
        })

        expect(commit).toBeCalledWith(SET_MEDIA, {
          media: [],
          mediaType: IMAGE,
        })
        done()
      })
    })

    it('FETCH_MEDIA does not reset images if page is defined', (done) => {
      const params = {
        q: 'foo',
        page: 1,
        shouldPersistMedia: false,
        mediaType: IMAGE,
      }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_MEDIA
      ]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).not.toBeCalledWith(SET_MEDIA, { media: [] })
        done()
      })
    })

    it('FETCH_IMAGE on success', (done) => {
      const params = { id: 'foo' }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_IMAGE
      ]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(commit).toBeCalledWith(SET_IMAGE, { image: {} })
        expect(commit).toBeCalledWith(FETCH_END_MEDIA, { mediaType: IMAGE })

        expect(commit).toBeCalledWith(SET_IMAGE, { image: imageDetailData })

        expect(imageServiceMock.getMediaDetail).toBeCalledWith(params)

        done()
      })
    })

    it('FETCH_IMAGE dispatches SEND_RESULT_CLICKED_EVENT', () => {
      const params = { id: 'foo' }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_IMAGE
      ]
      action({ commit, dispatch, state }, params)

      expect(dispatch).toHaveBeenLastCalledWith('SEND_RESULT_CLICKED_EVENT', {
        query: state.query.q,
        resultUuid: 'foo',
        resultRank: 0,
        sessionId: state.usageSessionId,
      })
    })

    it('FETCH_IMAGE on error', (done) => {
      const failedMock = {
        getMediaDetail: jest.fn(() => Promise.reject('error')),
      }
      const params = { id: 'foo' }
      const action = store.actions(failedMock, failedMock)[FETCH_IMAGE]
      action({ commit, dispatch, state }, params).catch((error) => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(dispatch).toBeCalledWith('HANDLE_IMAGE_ERROR', error)
      })
      done()
    })

    it('FETCH_IMAGE on 404 doesnt break and commits MEDIA_NOT_FOUND', (done) => {
      const failedMock = {
        getMediaDetail: jest.fn(() =>
          Promise.reject({ response: { status: 404 } })
        ),
      }
      const params = { id: 'foo' }
      const action = store.actions(failedMock, failedMock)[FETCH_IMAGE]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(commit).toBeCalledWith(MEDIA_NOT_FOUND, { mediaType: IMAGE })

        done()
      })
    })
  })
})
