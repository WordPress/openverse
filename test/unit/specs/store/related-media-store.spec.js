import store, { actionsCreator } from '~/store/related'
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
      const state = store.state()
      expect(state.audios).toHaveLength(0)
      expect(state.images).toHaveLength(0)
    })
  })

  describe('mutations', () => {
    let state = null
    const mutations = store.mutations

    beforeEach(() => {
      state = { images: [], audios: [] }
    })

    it('SET_RELATED_MEDIA updates state', () => {
      const params = {
        mediaType: IMAGE,
        relatedMedia: ['foo'],
      }
      mutations[SET_RELATED_MEDIA](state, params)
      expect(state.images).toBe(params.relatedMedia)
    })
  })

  describe('actions', () => {
    const searchData = { results: ['foo'], result_count: 1 }
    let imageServiceMock = null
    let commit = null
    let dispatch = null

    beforeEach(() => {
      imageServiceMock = {
        getRelatedMedia: jest.fn(() => Promise.resolve({ data: searchData })),
      }
      commit = jest.fn()
      dispatch = jest.fn()
    })

    it('FETCH_RELATED_MEDIA on success', (done) => {
      const params = { id: 'foo', mediaType: IMAGE }
      const actions = actionsCreator({
        [IMAGE]: imageServiceMock,
      })
      const action = actions[FETCH_RELATED_MEDIA]
      action({ commit, dispatch }, params).then(() => {
        expect(commit).toBeCalledWith(
          FETCH_START_MEDIA,
          { mediaType: IMAGE },
          { root: true }
        )
        expect(commit).toBeCalledWith(
          FETCH_END_MEDIA,
          { mediaType: IMAGE },
          { root: true }
        )

        expect(commit).toBeCalledWith(SET_RELATED_MEDIA, {
          mediaType: IMAGE,
          relatedMedia: searchData.results,
        })

        expect(imageServiceMock.getRelatedMedia).toBeCalledWith(params)
        done()
      })
    })

    it('FETCH_RELATED_IMAGES on error', (done) => {
      const imageServiceMock = {
        getRelatedMedia: jest.fn(() => Promise.reject('error')),
      }
      const params = { id: 'foo', mediaType: IMAGE }
      const actions = actionsCreator({
        [IMAGE]: imageServiceMock,
      })
      const action = actions[FETCH_RELATED_MEDIA]
      action({ commit, dispatch }, params).catch((error) => {
        expect(commit).toBeCalledWith(FETCH_START_MEDIA, { mediaType: IMAGE })
        expect(dispatch).toBeCalledWith('HANDLE_IMAGE_ERROR', error)
      })
      done()
    })
  })
})
