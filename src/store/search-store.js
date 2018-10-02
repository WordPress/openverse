
import ImageService from '@/api/ImageService';
import router from '@/router';
import { FETCH_IMAGES, FETCH_IMAGE, FETCH_RELATED_IMAGES } from './action-types';
import {
  FETCH_END_IMAGES,
  FETCH_IMAGES_ERROR,
  FETCH_START_IMAGES,
  SET_FILTER_IS_APPLIED,
  SET_FILTER_IS_VISIBLE,
  SET_IMAGE,
  SET_IMAGE_PAGE,
  SET_IMAGES,
  SET_IS_PAGE_CHANGE,
  SET_QUERY,
  SET_RELATED_IMAGES,
} from './mutation-types';

const state = {
  image: {},
  imagesCount: 0,
  imagePage: 1,
  images: [],
  isFetchingImages: false,
  isFetchingImagesError: true,
  isFilterVisible: false,
  isFilterApplied: false,
  query: { q: '' },
  relatedImages: [],
  relatedImagesCount: 0,
};

const actions = {
  [FETCH_IMAGES]({ commit }, params) {
    commit(FETCH_START_IMAGES);
    return ImageService.search(params)
      .then(({ data }) => {
        commit(FETCH_END_IMAGES);
        commit(SET_IMAGES,
          { images: data.results,
            imagesCount: data.result_count,
            shouldPersistImages: params.shouldPersistImages,
            page: params.page,
          },
        );

        if (params.query) {
          commit(SET_QUERY, { query: params.query });
        }
      })
      .catch((error) => {
        commit(FETCH_IMAGES_ERROR);
        throw new Error(error);
      });
  },
  [FETCH_IMAGE]({ commit }, params) {
    commit(FETCH_START_IMAGES);
    return ImageService.getImageDetail(params)
      .then(({ data }) => {
        commit(FETCH_END_IMAGES);
        commit(SET_IMAGE, { image: data });
      })
      .catch((error) => {
        commit(FETCH_IMAGES_ERROR);
        throw new Error(error);
      });
  },
  [FETCH_RELATED_IMAGES]({ commit }, params) {
    commit(FETCH_START_IMAGES);
    return ImageService.search(params)
      .then(({ data }) => {
        commit(FETCH_END_IMAGES);
        commit(SET_RELATED_IMAGES,
          { relatedImages: data.results,
            relatedImagesCount: data.result_count,
          },
        );
      })
      .catch((error) => {
        commit(FETCH_IMAGES_ERROR);
        throw new Error(error);
      });
  },
};

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [FETCH_START_IMAGES](_state) {
    _state.isFetchingImages = true;
    _state.isFetchingImagesError = false;
  },
  [FETCH_END_IMAGES](_state) {
    _state.isFetchingImages = false;
  },
  [FETCH_IMAGES_ERROR](_state) {
    _state.isFetchingImagesError = true;
    _state.isFetchingImages = false;
  },
  [SET_IMAGE](_state, params) {
    _state.image = params.image;
  },
  [SET_FILTER_IS_VISIBLE](_state, params) {
    _state.isFilterVisible = params.isFilterVisible;
  },
  [SET_FILTER_IS_APPLIED](_state, params) {
    _state.isFilterApplied = params.isFilterApplied;
  },
  [SET_IS_PAGE_CHANGE](_state, params) {
    _state.SET_IS_PAGE_CHANGE = params.isPageChange;
  },
  [SET_IMAGE_PAGE](_state, params) {
    _state.imagePage = params.imagePage;
  },
  [SET_IMAGE_PAGE](_state, params) {
    _state.imagePage = params.imagePage;
  },
  [SET_RELATED_IMAGES](_state, params) {
    _state.relatedImages = params.relatedImages;
    _state.relatedImagesCount = params.relatedImagesCount;
  },
  [SET_IMAGES](_state, params) {
    if (params.shouldPersistImages) {
      _state.images = _state.images.concat(params.images);
    } else {
      _state.images = params.images;
    }

    _state.imagesCount = params.imagesCount || 0;
    _state.imagePage = params.page || 1;
  },
  [SET_QUERY](_state, params) {
    let query;
    if (params.override) {
      query = params.query;
    } else {
      query = Object.assign({}, _state.query, params.query);
    }

    const isFilterApplied = ['li', 'provider', 'lt']
      .some(key => query[key] && query[key].length > 0);

    mutations[SET_FILTER_IS_APPLIED](_state, { isFilterApplied });

    if (params.shouldNavigate === true) {
      router.push({ path: 'search', query });
    } else {
      _state.query = query;
    }
  },
};

export default {
  state,
  actions,
  mutations,
};
