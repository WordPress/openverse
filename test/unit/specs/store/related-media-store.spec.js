import store from '~/store-modules/related-media-store'
import {
  FETCH_END_MEDIA,
  FETCH_START_MEDIA,
  SET_RELATED_MEDIA,
} from '~/constants/mutation-types'
import { FETCH_RELATED_MEDIA } from '~/constants/action-types'
import { IMAGE } from '~/constants/media'

describe('Related Images Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      const state = store.state
      expect(state.related.audios).toHaveLength(0)
      expect(state.related.images).toHaveLength(0)
    })
  })

  describe('mutations', () => {
    let state = null
    const mutations = store.mutations

    beforeEach(() => {
      state = { related: { images: [], audios: [] } }
    })

    it('SET_RELATED_MEDIA updates state', () => {
      const params = {
        mediaType: IMAGE,
        relatedMedia: ['foo'],
      }
      mutations[SET_RELATED_MEDIA](state, params)
      expect(state.relatedImages).toBe(params.relatedImages)
    })
  })

  describe('actions', () => {
    const searchData = { results: ['foo'], result_count: 1 }
    let audioServiceMock = null
    let imageServiceMock = null
    let commit = null
    let dispatch = null

    beforeEach(() => {
      audioServiceMock = {
        getRelatedMedia: jest.fn(() => Promise.resolve({ data: searchData })),
      }
      imageServiceMock = {
        getRelatedMedia: jest.fn(() => Promise.resolve({ data: searchData })),
      }
      commit = jest.fn()
      dispatch = jest.fn()
    })

    it('FETCH_RELATED_MEDIA on success', (done) => {
      const params = { id: 'foo', mediaType: IMAGE }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_RELATED_MEDIA
      ]
      action({ commit, dispatch }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(commit).toBeCalledWith(FETCH_END_MEDIA, { mediaType: IMAGE })

        expect(commit).toBeCalledWith(SET_RELATED_MEDIA, {
          mediaType: IMAGE,
          relatedMedia: searchData.results,
        })

        expect(imageServiceMock.getRelatedMedia).toBeCalledWith(params)
        done()
      })
    })

    it('FETCH_RELATED_IMAGES on error', (done) => {
      const audioServiceMock = {
        getRelatedMedia: jest.fn(() => Promise.reject('error')),
      }
      const imageServiceMock = {
        getRelatedMedia: jest.fn(() => Promise.reject('error')),
      }
      const params = { id: 'foo', mediaType: IMAGE }
      const action = store.actions(audioServiceMock, imageServiceMock)[
        FETCH_RELATED_MEDIA
      ]
      action({ commit, dispatch }, params).catch((error) => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(dispatch).toBeCalledWith('HANDLE_IMAGE_ERROR', error)
      })
      done()
    })
  })
})
