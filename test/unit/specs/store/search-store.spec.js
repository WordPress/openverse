import store from '@/store/search-store';
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
} from '@/store/mutation-types';
import { FETCH_IMAGES, FETCH_IMAGE, FETCH_RELATED_IMAGES } from '@/store/action-types';


describe('Search Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      const state = store.state('?q=');
      expect(state.imagesCount).toBe(0);
      expect(state.imagePage).toBe(1);
      expect(state.images).toHaveLength(0);
      expect(state.isFetchingImages).toBeFalsy();
      expect(state.isFetchingImagesError).toBeTruthy();
      expect(state.isFilterVisible).toBeFalsy();
      expect(state.isFilterApplied).toBeFalsy();
      expect(state.query.q).toBe('');
      expect(state.relatedImages).toHaveLength(0);
      expect(state.relatedImagesCount).toBe(0);
    });

    it('gets query from search params', () => {
      const state = store.state('?q=landscapes&provider=500px&li=by&lt=all&searchBy=creator');
      expect(state.imagesCount).toBe(0);
      expect(state.imagePage).toBe(1);
      expect(state.images).toHaveLength(0);
      expect(state.isFetchingImages).toBeFalsy();
      expect(state.isFetchingImagesError).toBeTruthy();
      expect(state.isFilterVisible).toBeFalsy();
      expect(state.isFilterApplied).toBeTruthy();
      expect(state.query.q).toBe('landscapes');
      expect(state.query.provider).toBe('500px');
      expect(state.query.li).toBe('by');
      expect(state.query.lt).toBe('all');
      expect(state.query.searchBy).toBe('creator');
      expect(state.relatedImages).toHaveLength(0);
      expect(state.relatedImagesCount).toBe(0);
    });

    it('isFilterApplied is set to true when provider filter is set', () => {
      const state = store.state('?q=landscapes&provider=500px&li=by&lt=');
      expect(state.isFilterApplied).toBeTruthy();
    });

    it('isFilterApplied is set to true when searchBy filter is set', () => {
      const state = store.state('?q=landscapes&searchBy=creator');
      expect(state.isFilterApplied).toBeTruthy();
    });

    it('isFilterApplied is set to true when license filter is set', () => {
      const state = store.state('?q=landscapes&li=by');
      expect(state.isFilterApplied).toBeTruthy();
    });

    it('isFilterApplied is set to true when license type filter is set', () => {
      const state = store.state('?q=landscapes&lt=all');
      expect(state.isFilterApplied).toBeTruthy();
    });

    it('isFilterApplied is set to false when no filter is set', () => {
      const state = store.state('?q=landscapes');
      expect(state.isFilterApplied).toBeFalsy();
    });
  });

  describe('mutations', () => {
    let state = null;
    const routePushMock = jest.fn();
    const mutations = store.mutations(routePushMock);

    beforeEach(() => {
      state = {};
    });

    it('FETCH_START_IMAGES updates state', () => {
      mutations[FETCH_START_IMAGES](state);

      expect(state.isFetchingImages).toBeTruthy();
      expect(state.isFetchingImagesError).toBeFalsy();
    });

    it('FETCH_END_IMAGES updates state', () => {
      mutations[FETCH_END_IMAGES](state);

      expect(state.isFetchingImages).toBeFalsy();
    });

    it('FETCH_IMAGES_ERROR updates state', () => {
      mutations[FETCH_IMAGES_ERROR](state);

      expect(state.isFetchingImages).toBeFalsy();
      expect(state.isFetchingImagesError).toBeTruthy();
    });

    it('SET_IMAGE updates state', () => {
      const params = { image: 'bar' };
      mutations[SET_IMAGE](state, params);

      expect(state.image).toBe(params.image);
    });

    it('SET_FILTER_IS_VISIBLE updates state', () => {
      const params = { isFilterVisible: 'bar' };
      mutations[SET_FILTER_IS_VISIBLE](state, params);

      expect(state.isFilterVisible).toBe(params.isFilterVisible);
    });

    it('SET_FILTER_IS_APPLIED updates state', () => {
      const params = { isFilterApplied: 'bar' };
      mutations[SET_FILTER_IS_APPLIED](state, params);

      expect(state.isFilterApplied).toBe(params.isFilterApplied);
    });

    it('SET_IMAGE_PAGE updates state', () => {
      const params = { imagePage: 'bar' };
      mutations[SET_IMAGE_PAGE](state, params);

      expect(state.imagePage).toBe(params.imagePage);
    });

    it('SET_RELATED_IMAGES updates state', () => {
      const params = { relatedImages: ['foo'], relatedImagesCount: 1 };
      mutations[SET_RELATED_IMAGES](state, params);

      expect(state.relatedImages).toBe(params.relatedImages);
      expect(state.relatedImagesCount).toBe(params.relatedImagesCount);
    });

    it('SET_IMAGES updates state persisting images', () => {
      state.images = ['img1'];
      const params = { images: ['img2'], imagesCount: 2, page: 2, shouldPersistImages: true };
      mutations[SET_IMAGES](state, params);

      expect(state.images).toEqual(['img1', 'img2']);
      expect(state.imagesCount).toBe(params.imagesCount);
      expect(state.imagePage).toBe(params.page);
    });

    it('SET_IMAGES updates state not persisting images', () => {
      state.images = ['img1'];
      const params = { images: ['img2'], imagesCount: 2, page: 2, shouldPersistImages: false };
      mutations[SET_IMAGES](state, params);

      expect(state.images).toEqual(['img2']);
      expect(state.imagesCount).toBe(params.imagesCount);
      expect(state.imagePage).toBe(params.page);
    });

    it('SET_IMAGES updates state with default count and page', () => {
      state.images = ['img1'];
      const params = { images: ['img2'] };
      mutations[SET_IMAGES](state, params);

      expect(state.imagesCount).toBe(0);
      expect(state.imagePage).toBe(1);
    });

    it('SET_QUERY updates state', () => {
      const params = { query: { q: 'foo' } };
      mutations[SET_QUERY](state, params);

      expect(state.query.q).toBe(params.query.q);
    });

    it('SET_QUERY updates isFilterApplied with provider', () => {
      const params = { query: { q: 'foo', provider: 'bar' } };
      mutations[SET_QUERY](state, params);

      expect(state.query.provider).toBe(params.query.provider);
      expect(state.isFilterApplied).toBeTruthy();
    });

    it('SET_QUERY updates isFilterApplied with license', () => {
      const params = { query: { q: 'foo', li: 'bar' } };
      mutations[SET_QUERY](state, params);

      expect(state.query.li).toBe(params.query.li);
      expect(state.isFilterApplied).toBeTruthy();
    });

    it('SET_QUERY updates isFilterApplied with license type', () => {
      const params = { query: { q: 'foo', lt: 'bar' } };
      mutations[SET_QUERY](state, params);

      expect(state.query.li).toBe(params.query.li);
      expect(state.isFilterApplied).toBeTruthy();
    });

    it('SET_QUERY updates isFilterApplied with searchBy', () => {
      const params = { query: { q: 'foo', searchBy: 'creator' } };
      mutations[SET_QUERY](state, params);

      expect(state.query.searchBy).toBe(params.query.searchBy);
      expect(state.isFilterApplied).toBeTruthy();
    });

    it('SET_QUERY pushes route when shouldNavigate is true', () => {
      const params = { query: { q: 'foo', lt: 'bar' }, shouldNavigate: true };
      mutations[SET_QUERY](state, params);

      expect(routePushMock).toBeCalledWith({ path: 'search', query: params.query });
    });
  });

  describe('actions', () => {
    const searchData = { results: ['foo'], result_count: 1 };
    const imageDetailData = 'imageDetails';
    const imageServiceMock = {
      search: jest.fn(() => Promise.resolve({ data: searchData })),
      getImageDetail: jest.fn(() => Promise.resolve({ data: imageDetailData })),
    };
    const commit = jest.fn();
    it('FETCH_IMAGES on success', (done) => {
      const params = { query: { q: 'foo' }, page: 1, shouldPersistImages: false };
      const action = store.actions(imageServiceMock)[FETCH_IMAGES];
      action({ commit }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES);
        expect(commit).toBeCalledWith(FETCH_END_IMAGES);

        expect(commit).toBeCalledWith(SET_IMAGES, {
          images: searchData.results,
          imagesCount: searchData.result_count,
          shouldPersistImages: params.shouldPersistImages,
          page: params.page,
        });

        expect(imageServiceMock.search).toBeCalledWith(params);

        expect(commit).toBeCalledWith(SET_QUERY, { query: params.query });
        done();
      });
    });

    it('FETCH_IMAGES on error', (done) => {
      const failedMock = {
        search: jest.fn(() => Promise.reject('error')),
      };
      const params = { query: { q: 'foo' }, page: 1, shouldPersistImages: false };
      const action = store.actions(failedMock)[FETCH_IMAGES];
      action({ commit }, params).catch(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES);
        expect(commit).toBeCalledWith(FETCH_IMAGES_ERROR);
        done();
      });
    });

    it('FETCH_IMAGE on success', (done) => {
      const params = 'foo';
      const action = store.actions(imageServiceMock)[FETCH_IMAGE];
      action({ commit }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES);
        expect(commit).toBeCalledWith(FETCH_END_IMAGES);

        expect(commit).toBeCalledWith(SET_IMAGE, { image: imageDetailData });

        expect(imageServiceMock.getImageDetail).toBeCalledWith(params);

        done();
      });
    });

    it('FETCH_IMAGE on error', (done) => {
      const failedMock = {
        getImageDetail: jest.fn(() => Promise.reject('error')),
      };
      const params = 'foo';
      const action = store.actions(failedMock)[FETCH_IMAGE];
      action({ commit }, params).catch(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES);
        expect(commit).toBeCalledWith(FETCH_IMAGES_ERROR);

        done();
      });
    });

    it('FETCH_RELATED_IMAGES on success', (done) => {
      const params = { query: { q: 'foo' }, page: 1, shouldPersistImages: false };
      const action = store.actions(imageServiceMock)[FETCH_RELATED_IMAGES];
      action({ commit }, params).then(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES);
        expect(commit).toBeCalledWith(FETCH_END_IMAGES);

        expect(commit).toBeCalledWith(SET_RELATED_IMAGES, {
          relatedImages: searchData.results,
          relatedImagesCount: searchData.result_count,
        });

        expect(imageServiceMock.search).toBeCalledWith(params);
        done();
      });
    });

    it('FETCH_RELATED_IMAGES on error', (done) => {
      const failedMock = {
        search: jest.fn(() => Promise.reject('error')),
      };
      const params = 'foo';
      const action = store.actions(failedMock)[FETCH_RELATED_IMAGES];
      action({ commit }, params).catch(() => {
        expect(commit).toBeCalledWith(FETCH_START_IMAGES);
        expect(commit).toBeCalledWith(FETCH_IMAGES_ERROR);

        done();
      });
    });
  });
});
