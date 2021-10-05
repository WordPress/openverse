import {
  FETCH_END_MEDIA,
  FETCH_START_MEDIA,
  SET_RELATED_MEDIA,
} from '~/constants/mutation-types'
import {
  FETCH_RELATED_MEDIA,
  HANDLE_NO_MEDIA,
  HANDLE_MEDIA_ERROR,
} from '~/constants/action-types'
import AudioService from '~/data/audio-service'
import ImageService from '~/data/image-service'
import { AUDIO, IMAGE } from '~/constants/media'

export const state = () => ({
  images: [],
  audios: [],
})

export const createActions = (services) => ({
  [FETCH_RELATED_MEDIA]({ commit, dispatch }, params) {
    const { mediaType } = params
    commit(FETCH_START_MEDIA, { mediaType }, { root: true })
    if (!Object.keys(services).includes(mediaType)) {
      throw new Error(
        `Unsupported media type ${mediaType} for related media fetching`
      )
    }
    const service = services[mediaType]
    return service
      .getRelatedMedia(params)
      .then(({ data }) => {
        commit(FETCH_END_MEDIA, { mediaType }, { root: true })
        commit(SET_RELATED_MEDIA, {
          mediaType,
          relatedMedia: data.results,
        })
        dispatch(
          HANDLE_NO_MEDIA,
          {
            mediaCount: data.results.length,
            mediaType,
          },
          { root: true }
        )
      })
      .catch((error) => {
        dispatch(
          HANDLE_MEDIA_ERROR,
          {
            mediaType,
            error,
          },
          { root: true }
        )
      })
  },
})

const services = {
  [AUDIO]: AudioService,
  [IMAGE]: ImageService,
}

export const actions = createActions(services)

export const mutations = {
  /**
   * @param _state
   * @param {'image'|'audio'} mediaType
   * @param {Array} relatedMedia
   */
  [SET_RELATED_MEDIA](_state, { mediaType, relatedMedia }) {
    _state[`${mediaType}s`] = relatedMedia
  },
}

export default {
  state,
  mutations,
  actions,
}
