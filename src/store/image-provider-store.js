
import ImageProviderService from '@/api/ImageProviderService';
import {
  FETCH_IMAGE_STATS,
} from './action-types';

import {
  FETCH_IMAGE_STATS_END,
  SET_FETCH_IMAGES_ERROR,
  FETCH_IMAGE_STATS_START,
  SET_IMAGE_STATS,
} from './mutation-types';

const state = {
  imageStats: [],
  isFetchingImageStatsError: false,
  isFetchingImageStats: false,
};

const actions = {
  [FETCH_IMAGE_STATS]({ commit }, params) {
    commit(SET_FETCH_IMAGES_ERROR, { isFetchingImageStatsError: true });
    commit(FETCH_IMAGE_STATS_START);
    return ImageProviderService.getProviderStats(params)
      .then(({ data }) => {
        commit(FETCH_IMAGE_STATS_END);
        commit(SET_IMAGE_STATS,
          { imageStats: data },
        );
      })
      .catch((error) => {
        commit(SET_FETCH_IMAGES_ERROR, { isFetchingImageStatsError: true });
        throw new Error(error);
      });
  },
};

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [FETCH_IMAGE_STATS_START](_state) {
    _state.isFetchingImageStats = true;
  },
  [FETCH_IMAGE_STATS_END](_state) {
    _state.isFetchingImageStats = false;
  },
  [SET_FETCH_IMAGES_ERROR](_state, params) {
    _state.isFetchingImageStatsError = params.isFetchingImageStatsError;
  },
  [SET_IMAGE_STATS](_state, params) {
    _state.imageStats = params.imageStats;
  },
};

export default {
  state,
  actions,
  mutations,
};
