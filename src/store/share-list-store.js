
import ShareListService from '@/api/ShareListService';
import {
  ADD_IMAGE_TO_LIST,
  CREATE_LIST,
  FETCH_LIST,
  FETCH_LISTS,
  REMOVE_IMAGE_FROM_LIST,
} from './action-types';

import {
  SELECT_IMAGE_FOR_LIST,
  FETCH_START,
  FETCH_END,
  SET_SHARE_LIST,
  SET_SHARE_LISTS,
  SET_SHARE_URL,
  UNSET_SHARE_URL,
} from './mutation-types';

const state = {
  selectedImages: [],
  shareLists: [],
  shareListImages: [],
  shareListURL: '',
  isFetching: false,
  isListClean: true,
};


const actions = {
  [CREATE_LIST]({ commit }, params) {
    commit(FETCH_START);

    return ShareListService.createList(params)
      .then(({ lists }) => {
        commit(FETCH_END);
        commit(SET_SHARE_LISTS, { shareLists: lists });
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
        commit(SET_SHARE_LIST, { shareListImages: data.images });
      })
      .catch((error) => {
        throw new Error(error);
      });
  },
  [FETCH_LISTS]({ commit }) {
    commit(FETCH_START);

    return ShareListService.getListsFromLocalStorage()
      .then((lists) => {
        commit(FETCH_END);
        commit(SET_SHARE_LISTS, { shareLists: lists });
      })
      .catch((error) => {
        throw new Error(error);
      });
  },
  [ADD_IMAGE_TO_LIST]({ commit }, params) {
    commit(FETCH_START);

    return ShareListService.getList(params)
      .then(({ data }) => {
        let imageIDs = [params.selectedImageID];

        if (data.images) {
          imageIDs = imageIDs.concat(data.images.map(image => image.id));
        }

        return ShareListService.updateList(
          { auth: params.auth, id: params.id, images: imageIDs },
        )
        .then(() => {
          actions.FETCH_LIST({ commit }, params);
          commit(FETCH_END);
        });
      })
      .catch((error) => {
        throw new Error(error);
      });
  },
  [REMOVE_IMAGE_FROM_LIST]({ commit }, params) {
    commit(FETCH_START);
    const images = params.shareListImages;
    const imageIDs = [];

    images.forEach((image, index) => {
      if (image.id !== params.imageID) {
        imageIDs.push(image.id);
      }
    });

    return ShareListService.updateList(
      { auth: params.auth, id: params.id, images: imageIDs })
      .then(() => {
        actions.FETCH_LIST({ commit }, params);
        commit(FETCH_END) ;
      })
      .catch((error) => {
        throw new Error(error);
      });
  },
};

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [SELECT_IMAGE_FOR_LIST](_state, params) {
    const duplicateImage = _state.shareListImages.find(image => image.id === params.image.id);
    let UNDEFINED;

    if (duplicateImage === UNDEFINED) {
      _state.selectedImages.unshift(params.image);
    }

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
    const shareID = params.url.match(/\/(?:list\/)(.*)/)[1];
    const shareURL = `/lists/${shareID}`;
    _state.shareListURL = location.origin + shareURL;
  },
  [UNSET_SHARE_URL](_state) {
    _state.shareListURL = '';
  },
  [SET_SHARE_LIST](_state, params) {
    _state.shareListImages = params.shareListImages;
  },
  [SET_SHARE_LISTS](_state, params) {
    _state.shareLists = params.shareLists;
  },
};

export default {
  state,
  actions,
  mutations,
};
