import LinkService from '@/api/LinkService';
import ShareListService from '@/api/ShareListService';

import {
  ADD_IMAGE_TO_LIST,
  CREATE_LIST,
  CREATE_LIST_SHORTENED_URL,
  FETCH_LIST,
  FETCH_LISTS,
  REMOVE_IMAGE_FROM_LIST,
  REMOVE_LIST,
} from './action-types';

import {
  ADD_IMAGE_TO_LIST_END,
  FETCH_END,
  FETCH_START,
  SELECT_IMAGE_FOR_LIST,
  SET_SHARE_LIST,
  SET_SHARE_LISTS,
  SET_SHARE_URL,
  UNSET_SHARE_URL,
} from './mutation-types';

const state = {
  isFetching: false,
  shareListImages: [],
  shareLists: [],
  shareListSelectedImage: {},
  shareListURL: '',
};

const actions = {
  [CREATE_LIST]({ commit }, params) {
    commit(FETCH_START);

    return ShareListService.createList(params)
      .then(({ lists }) => {
        commit(FETCH_END);
        commit(SET_SHARE_LISTS, { shareLists: lists });
        commit(ADD_IMAGE_TO_LIST_END);
      })
      .catch((error) => {
        commit(FETCH_END);
        throw new Error(error);
      });
  },
  [CREATE_LIST_SHORTENED_URL]({ commit }, params) {
    commit(FETCH_START);

    return LinkService.createLink(params)
      .then(({ data }) => {
        commit(FETCH_END);
        commit(SET_SHARE_URL, { shortenedURL: data.shortened_url });
      })
      .catch((error) => {
        commit(FETCH_END);
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
        commit(FETCH_END);
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
        commit(FETCH_END);
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
            commit(ADD_IMAGE_TO_LIST_END);
          });
      })
      .catch((error) => {
        commit(FETCH_END);
        throw new Error(error);
      });
  },
  [REMOVE_LIST]({ commit }, params) {
    commit(FETCH_START);
    return ShareListService.deleteList(
      { auth: params.auth, id: params.listID })
      .then(() => {
        ShareListService.deleteListFromLocalStorage(params.listID)
          .then((lists) => {
            commit(SET_SHARE_LISTS, { shareLists: lists });
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

    images.forEach((image) => {
      if (image.id !== params.imageID) {
        imageIDs.push(image.id);
      }
    });

    return ShareListService.updateList(
      { auth: params.auth, id: params.id, images: imageIDs })
      .then(() => {
        actions.FETCH_LIST({ commit }, params);
        commit(FETCH_END);
      })
      .catch((error) => {
        commit(FETCH_END);
        throw new Error(error);
      });
  },

};

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [SELECT_IMAGE_FOR_LIST](_state, params) {
    _state.shareListSelectedImage = params.image;
  },
  [FETCH_START](_state) {
    _state.isFetching = true;
  },
  [FETCH_END](_state) {
    _state.isFetching = false;
  },
  [SET_SHARE_URL](_state, params) {
    _state.shareListURL = `${window.location.protocol}//${params.shortenedURL}`;
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
