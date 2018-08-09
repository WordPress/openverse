
import ShareListService from '@/api/ShareListService';
import { FETCH_LIST, CREATE_LIST } from './action-types';
import { ADD_IMAGE_TO_LIST,
  REMOVE_IMAGE_FROM_LIST,
  FETCH_START, FETCH_END,
  SET_SHARE_LIST,
  SET_SHARE_URL,
  UNSET_SHARE_URL } from './mutation-types';

const state = {
  shareListImages: [],
  shareListURL: '',
  isFetching: false,
  isListClean: true,
};

const actions = {
  [CREATE_LIST]({ commit }, params) {
    commit(FETCH_START);
    return ShareListService.createList(params)
      .then(({ data }) => {
        commit(FETCH_END);
        commit(SET_SHARE_URL, { url: data.url });
      })
      .catch((error) => {
        throw new Error(error);
      });
  },
  [FETCH_LIST]({ commit }, params) {
    commit(FETCH_START);
    return ShareListService.getList(params)
      .then(({ data }) => {
        commit(FETCH_END);
        commit(SET_SHARE_LIST, { shareListImages: data.results });
      })
      .catch((error) => {
        throw new Error(error);
      });
  },
};

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [ADD_IMAGE_TO_LIST](_state, params) {
    const duplicateImage = _state.shareListImages.find(image => image.id === params.image.id);
    let UNDEFINED;

    if (duplicateImage === UNDEFINED) {
      _state.shareListImages.unshift(params.image);
    }

    if (_state.shareListURL) {
      _state.isListClean = false;
    }
    _state.shareListURL = '';
  },
  [REMOVE_IMAGE_FROM_LIST](_state, params) {
    _state.shareListImages.forEach((image, index) => {
      if (image.id === params.image.id) {
        _state.shareListImages.splice(index, 1);
      }
    });

    if (_state.shareListURL) {
      _state.isListClean = false;
    }
    _state.shareListURL = '';
  },
  [FETCH_START](_state) {
    _state.isFetching = true;
  },
  [FETCH_END](_state) {
    _state.isFetching = false;
  },
  [SET_SHARE_URL](_state, params) {
    const shareID = params.url.match(/(?:list\/)(\d*)/)[1];
    const shareURL = `/lists/${shareID}`;
    _state.shareListURL = location.origin + shareURL;
  },
  [UNSET_SHARE_URL](_state) {
    _state.shareListURL = '';
  },
  [SET_SHARE_LIST](_state, params) {
    _state.shareListImages = params.shareListImages;
  },
};

export default {
  state,
  actions,
  mutations,
};
