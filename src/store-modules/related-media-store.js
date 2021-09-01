import {
  FETCH_END_MEDIA,
  FETCH_START_MEDIA,
  SET_RELATED_MEDIA,
} from './mutation-types'
import {
  FETCH_RELATED_MEDIA,
  HANDLE_NO_MEDIA,
  HANDLE_IMAGE_ERROR,
} from './action-types'
import { AUDIO, IMAGE } from '~/constants/media'

const initialState = {
  related: {
    images: [],
    audios: [],
  },
}

const actions = (AudioService, ImageService) => ({
  [FETCH_RELATED_MEDIA]({ commit, dispatch }, params) {
    const { mediaType } = params
    commit(FETCH_START_MEDIA, { mediaType })
    let service
    if (mediaType === AUDIO) {
      service = AudioService
    } else if (mediaType === IMAGE) {
      service = ImageService
    } else {
      throw new Error(
        `Unsupported media type ${mediaType} for related media fetching`
      )
    }
    return service
      .getRelatedMedia(params)
      .then(({ data }) => {
        commit(FETCH_END_MEDIA, { mediaType })
        commit(SET_RELATED_MEDIA, {
          mediaType,
          relatedMedia: data.results,
        })
        dispatch(HANDLE_NO_MEDIA, {
          mediaCount: data.results.length,
          mediaType,
        })
      })
      .catch((error) => {
        dispatch(HANDLE_IMAGE_ERROR, error)
      })
  },
})

const mutations = {
  /**
   * @param _state
   * @param {'image'|'audio'} mediaType
   * @param {Array} relatedMedia
   */
  [SET_RELATED_MEDIA](_state, { mediaType, relatedMedia }) {
    _state.related[`${mediaType}s`] = relatedMedia
  },
}

export default {
  state: initialState,
  actions,
  mutations,
}
