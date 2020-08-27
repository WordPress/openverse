import {
  FETCH_END_IMAGES,
  FETCH_START_IMAGES,
  HANDLE_NO_IMAGES,
  SET_RELATED_IMAGES,
} from '../store/mutation-types'
import { FETCH_RELATED_IMAGES, HANDLE_IMAGE_ERROR } from '../store/action-types'

const initialState = {
  relatedImages: [],
  relatedImagesCount: 0,
}

const actions = (ImageService) => ({
  [FETCH_RELATED_IMAGES]({ commit, dispatch }, params) {
    commit(FETCH_START_IMAGES)
    return ImageService.getRelatedImages(params)
      .then(({ data }) => {
        commit(FETCH_END_IMAGES)
        commit(SET_RELATED_IMAGES, {
          relatedImages: data.results,
          relatedImagesCount: data.result_count,
        })
        dispatch(HANDLE_NO_IMAGES, data.results)
      })
      .catch((error) => {
        dispatch(HANDLE_IMAGE_ERROR, error)
      })
  },
})

/* eslint-disable no-param-reassign */
const mutations = {
  [SET_RELATED_IMAGES](_state, params) {
    _state.relatedImages = params.relatedImages
    _state.relatedImagesCount = params.relatedImagesCount
  },
}

export default {
  state: initialState,
  actions,
  mutations,
}
