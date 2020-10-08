import store from '~/store-modules/search-store'
import {
  FETCH_END_IMAGES,
  FETCH_IMAGES_ERROR,
  FETCH_START_IMAGES,
  SET_IMAGE,
  SET_IMAGE_PAGE,
  SET_IMAGES,
  SET_QUERY,
  IMAGE_NOT_FOUND,
} from '~/store-modules/mutation-types'
import {
  FETCH_IMAGES,
  FETCH_IMAGE,
  FETCH_COLLECTION_IMAGES,
} from '~/store-modules/action-types'

describe('Search Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      const state = store.state
      expect(state.imagesCount).toBe(0)
      expect(state.imagePage).toBe(1)
      expect(state.images).toHaveLength(0)
      expect(state.isFetchingImages).toBeFalsy()
      expect(state.isFetchingImagesError).toBeTruthy()
      expect(state.query.q).toBe(undefined)
      expect(state.errorMsg).toBe(null)
    })
  })

  describe('mutations', () => {
    let state = null
    const mutations = store.mutations

    beforeEach(() => {
      state = {}
    })

    it('FETCH_START_IMAGES updates state', () => {
      mutations[FETCH_START_IMAGES](state)

      expect(state.isFetchingImages).toBeTruthy()
      expect(state.isFetchingImagesError).toBeFalsy()
    })

    it('FETCH_END_IMAGES updates state', () => {
      mutations[FETCH_END_IMAGES](state)

      expect(state.isFetchingImages).toBeFalsy()
    })

    it('FETCH_IMAGES_ERROR updates state', () => {
      mutations[FETCH_IMAGES_ERROR](state, { errorMsg: 'error' })

      expect(state.isFetchingImages).toBeFalsy()
      expect(state.isFetchingImagesError).toBeTruthy()
      expect(state.errorMsg).toBe('error')
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

    it('SET_IMAGES updates state persisting images', () => {
      const img1 = { title: 'Foo', creator: 'foo', tags: [] }
      const img2 = { title: 'Bar', creator: 'bar', tags: [] }
      state.images = [img1]
      const params = {
        images: [img2],
        imagesCount: 2,
        page: 2,
        shouldPersistImages: true,
      }
      mutations[SET_IMAGES](state, params)

      expect(state.images).toEqual([img1, img2])
      expect(state.imagesCount).toBe(params.imagesCount)
      expect(state.imagePage).toBe(params.page)
    })

    it('SET_IMAGES updates state not persisting images', () => {
      const img = { title: 'Foo', creator: 'bar', tags: [] }
      state.images = ['img1']
      const params = {
        images: [img],
        imagesCount: 2,
        page: 2,
        shouldPersistImages: false,
      }
      mutations[SET_IMAGES](state, params)

      expect(state.images).toEqual([img])
      expect(state.imagesCount).toBe(params.imagesCount)
      expect(state.imagePage).toBe(params.page)
    })

    it('SET_IMAGES updates state with default count and page', () => {
      const img = { title: 'Foo', creator: 'bar', tags: [] }
      state.images = ['img1']
      const params = { images: [img] }
      mutations[SET_IMAGES](state, params)

      expect(state.imagesCount).toBe(0)
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
        getImageDetail: jest.fn(() =>
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

    it('FETCH_IMAGES on success', (done) => {
      const params = { q: 'foo', page: 1, shouldPersistImages: false }
      const action = store.actions(imageServiceMock)[FETCH_IMAGES]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES)
        expect(commit).toBeCalledWith(FETCH_END_IMAGES)

        expect(commit).toBeCalledWith(SET_IMAGES, {
          images: searchData.results,
          imagesCount: searchData.result_count,
          shouldPersistImages: params.shouldPersistImages,
          page: params.page,
        })

        expect(imageServiceMock.search).toBeCalledWith(params)

        done()
      })
    })

    it('FETCH_IMAGES dispatches SEND_SEARCH_QUERY_EVENT', () => {
      const params = { q: 'foo', shouldPersistImages: false }
      const action = store.actions(imageServiceMock)[FETCH_IMAGES]
      action({ commit, dispatch, state }, params)

      expect(dispatch).toHaveBeenLastCalledWith('SEND_SEARCH_QUERY_EVENT', {
        query: params.q,
        sessionId: state.usageSessionId,
      })
    })

    it('does not dispatch SEND_SEARCH_QUERY_EVENT if page param is available', () => {
      const params = { q: 'foo', page: 1, shouldPersistImages: false }
      const action = store.actions(imageServiceMock)[FETCH_IMAGES]
      action({ commit, dispatch, state }, params)

      expect(dispatch).not.toHaveBeenLastCalledWith('SEND_SEARCH_QUERY_EVENT', {
        query: params.q,
        sessionId: state.usageSessionId,
      })
    })

    it('FETCH_COLLECTION_IMAGES on success', (done) => {
      const params = { provider: 'met', page: 1, shouldPersistImages: false }
      const action = store.actions(imageServiceMock)[FETCH_COLLECTION_IMAGES]
      action({ commit, dispatch }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES)
        expect(commit).toBeCalledWith(FETCH_END_IMAGES)

        expect(commit).toBeCalledWith(SET_IMAGES, {
          images: searchData.results,
          imagesCount: searchData.result_count,
          shouldPersistImages: params.shouldPersistImages,
          page: params.page,
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
        shouldPersistImages: false,
      }
      const action = store.actions(imageServiceMock)[FETCH_COLLECTION_IMAGES]
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
        shouldPersistImages: false,
      }
      const action = store.actions(imageServiceMock)[FETCH_COLLECTION_IMAGES]
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
        shouldPersistImages: false,
      }
      const action = store.actions(imageServiceMock)[FETCH_COLLECTION_IMAGES]
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
        shouldPersistImages: false,
      }
      const action = store.actions(imageServiceMock)[FETCH_COLLECTION_IMAGES]
      action({ commit, dispatch }, params).then(() => {
        const newParams = { ...params, source: params.provider }
        delete newParams.provider
        expect(imageServiceMock.search).toBeCalledWith(newParams)

        done()
      })
    })

    it('FETCH_IMAGES on error', (done) => {
      const failedMock = {
        search: jest.fn(() => Promise.reject('error')),
      }
      const params = { q: 'foo', page: 1, shouldPersistImages: false }
      const action = store.actions(failedMock)[FETCH_IMAGES]
      action({ commit, dispatch, state }, params).catch((error) => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES)
        expect(dispatch).toBeCalledWith('HANDLE_IMAGE_ERROR', error)
      })
      done()
    })

    it('FETCH_COLLECTION_IMAGES on error', (done) => {
      const failedMock = {
        getProviderCollection: jest.fn(() => Promise.reject('error')),
        search: jest.fn(() => Promise.reject('error')),
      }
      const params = { q: 'foo', page: 1, shouldPersistImages: false }
      const action = store.actions(failedMock)[FETCH_COLLECTION_IMAGES]
      action({ commit, dispatch }, params).catch((error) => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES)
        expect(dispatch).toBeCalledWith('HANDLE_IMAGE_ERROR', error)
      })
      done()
    })

    it('FETCH_IMAGES resets images if page is not defined', (done) => {
      const params = { q: 'foo', page: undefined, shouldPersistImages: false }
      const action = store.actions(imageServiceMock)[FETCH_IMAGES]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).toBeCalledWith(SET_IMAGES, { images: [] })
        done()
      })
    })

    it('FETCH_IMAGES does not reset images if page is defined', (done) => {
      const params = { q: 'foo', page: 1, shouldPersistImages: false }
      const action = store.actions(imageServiceMock)[FETCH_IMAGES]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).not.toBeCalledWith(SET_IMAGES, { images: [] })
        done()
      })
    })

    it('FETCH_IMAGE on success', (done) => {
      const params = { id: 'foo' }
      const action = store.actions(imageServiceMock)[FETCH_IMAGE]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES)
        expect(commit).toBeCalledWith(SET_IMAGE, { image: {} })
        expect(commit).toBeCalledWith(FETCH_END_IMAGES)

        expect(commit).toBeCalledWith(SET_IMAGE, { image: imageDetailData })

        expect(imageServiceMock.getImageDetail).toBeCalledWith(params)

        done()
      })
    })

    it('FETCH_IMAGE dispatches SEND_RESULT_CLICKED_EVENT', () => {
      const params = { id: 'foo' }
      const action = store.actions(imageServiceMock)[FETCH_IMAGE]
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
        getImageDetail: jest.fn(() => Promise.reject('error')),
      }
      const params = { id: 'foo' }
      const action = store.actions(failedMock)[FETCH_IMAGE]
      action({ commit, dispatch, state }, params).catch((error) => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES)
        expect(dispatch).toBeCalledWith('HANDLE_IMAGE_ERROR', error)
      })
      done()
    })

    it('FETCH_IMAGE on 404 doesnt break and commits IMAGE_NOT_FOUND', (done) => {
      const failedMock = {
        getImageDetail: jest.fn(() =>
          Promise.reject({ response: { status: 404 } })
        ),
      }
      const params = { id: 'foo' }
      const action = store.actions(failedMock)[FETCH_IMAGE]
      action({ commit, dispatch, state }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES)
        expect(commit).toBeCalledWith(IMAGE_NOT_FOUND)

        done()
      })
    })
  })
})
