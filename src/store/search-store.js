
import ImageService from '@/api/ImageService';
import { FETCH_IMAGES, FETCH_IMAGE } from './action-types';
import { FETCH_START,
  FETCH_END,
  SET_IMAGES,
  SET_IMAGE,
  SET_IMAGE_PAGE,
  SET_GRID_FILTER,
  SET_QUERY } from './mutation-types';

const state = {
  filters: {},
  image: {},
  imageCount: 0,
  imagePage: 1,
  images: [],
  isFetching: false,
  query: { q: '' },
};

let UNDEFINED;

const actions = {
  [FETCH_IMAGES]({ commit }, params) {
    commit(FETCH_START);
    return ImageService.search(params)
      .then(({ data }) => {
        commit(FETCH_END);
        commit(SET_IMAGES,
          { images: data.results,
            imagesCount: data.result_count,
            shouldPersistImages: params.shouldPersistImages,
          }
        );

        if (params.page === UNDEFINED) {
          commit(SET_IMAGE_PAGE, { imagePage: 1 } );
        }

        if (params.q) {
          commit(SET_QUERY, params);
        }
      })
      .catch((error) => {
        throw new Error(error);
      });
  },
  [FETCH_IMAGE]({ commit }, params) {
    commit(FETCH_START);
    return ImageService.getImageDetail(params)
      .then(({ data }) => {
        commit(FETCH_END);
        commit(SET_IMAGE, { image: data });
      })
      .catch((error) => {
        throw new Error(error);
      });
  },
};

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [FETCH_START](_state) {
    _state.isFetching = true;
  },
  [FETCH_END](_state) {
    _state.isFetching = false;
  },
  [SET_IMAGE](_state, params) {
    _state.image = params.image;
  },
  [SET_IMAGE_PAGE](_state, params) {
    _state.imagePage = params.imagePage;
  },
  [SET_GRID_FILTER](_state, params) {
    _state.filter = params.filter;
  },
  [SET_IMAGES](_state, params) {
    if (params.shouldPersistImages) {
      _state.images = _state.images.concat(params.images);
    } else {
      _state.images = params.images;
    }

    _state.imagesCount = params.imagesCount;
  },
  [SET_QUERY](_state, params) {
    _state.query.q = params.q;
  },
};

export default {
  state,
  actions,
  mutations,
};
