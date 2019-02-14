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
      expect(store.state.imagesCount).toBe(0);
      expect(store.state.imagePage).toBe(1);
      expect(store.state.images).toHaveLength(0);
      expect(store.state.isFetchingImages).toBeFalsy();
      expect(store.state.isFetchingImagesError).toBeTruthy();
      expect(store.state.isFilterVisible).toBeFalsy();
      expect(store.state.isFilterApplied).toBeFalsy();
      expect(store.state.query.q).toBe('');
      expect(store.state.relatedImages).toHaveLength(0);
      expect(store.state.relatedImagesCount).toBe(0);
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
  });

  describe('actions', () => {
    const data = 'foobar';
    const imageProviderServiceMock = {
      getProviderStats: jest.fn(() => Promise.resolve({ data })),
    };
    const commit = jest.fn();
    // it('FETCH_IMAGE_STATS on success', (done) => {
    //   const action = store.actions(imageProviderServiceMock)[FETCH_IMAGE_STATS];
    //   action({ commit }, {}).then(() => {
    //     expect(commit).toBeCalledWith(SET_FETCH_IMAGES_ERROR, { isFetchingImageStatsError: false });
    //     expect(commit).toBeCalledWith(FETCH_IMAGE_STATS_START);

    //     expect(imageProviderServiceMock.getProviderStats).toBeCalled();

    //     expect(commit).toBeCalledWith(FETCH_IMAGE_STATS_END);
    //     expect(commit).toBeCalledWith(SET_IMAGE_STATS, { imageStats: data });
    //     done();
    //   });
    // });
  });
});
