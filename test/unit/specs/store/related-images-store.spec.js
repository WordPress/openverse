import store from '~/store-modules/related-images-store'
import {
  FETCH_END_IMAGES,
  FETCH_START_IMAGES,
  SET_RELATED_IMAGES,
} from '~/store-modules/mutation-types'
import { FETCH_RELATED_IMAGES } from '~/store-modules/action-types'

describe('Related Images Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      const state = store.state
      expect(state.relatedImages).toHaveLength(0)
      expect(state.relatedImagesCount).toBe(0)
    })
  })

  describe('mutations', () => {
    let state = null
    const mutations = store.mutations

    beforeEach(() => {
      state = {}
    })

    it('SET_RELATED_IMAGES updates state', () => {
      const params = { relatedImages: ['foo'], relatedImagesCount: 1 }
      mutations[SET_RELATED_IMAGES](state, params)
      expect(state.relatedImages).toBe(params.relatedImages)
      expect(state.relatedImagesCount).toBe(params.relatedImagesCount)
    })
  })

  describe('actions', () => {
    const searchData = { results: ['foo'], result_count: 1 }
    let params = null
    let commit = null
    let dispatch = null

    beforeEach(() => {
      params = { id: 'foo' }
      commit = jest.fn()
      dispatch = jest.fn()
    })

    it('FETCH_RELATED_IMAGES on success', (done) => {
      const imageServiceMock = {
        getRelatedImages: jest.fn(() => Promise.resolve({ data: searchData })),
      }
      const action = store.actions(imageServiceMock)[FETCH_RELATED_IMAGES]
      action({ commit, dispatch }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES)
        expect(commit).toBeCalledWith(FETCH_END_IMAGES)

        expect(commit).toBeCalledWith(SET_RELATED_IMAGES, {
          relatedImages: searchData.results,
          relatedImagesCount: searchData.result_count,
        })

        expect(imageServiceMock.getRelatedImages).toBeCalledWith(params)
        done()
      })
    })

    it('FETCH_RELATED_IMAGES on error', (done) => {
      const imageServiceMock = {
        getRelatedImages: jest.fn(() => Promise.reject('error')),
      }
      const action = store.actions(imageServiceMock)[FETCH_RELATED_IMAGES]
      action({ commit }, params).catch((error) => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES)
        expect(dispatch).toBeCalledWith('HANDLE_IMAGE_ERROR', error)
      })
      done()
    })
  })
})
