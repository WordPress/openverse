import store from '@/store/image-provider-store';
import {
  FETCH_IMAGE_STATS_END,
  SET_FETCH_IMAGES_ERROR,
  FETCH_IMAGE_STATS_START,
  SET_IMAGE_STATS,
} from '@/store/mutation-types';
import {
  FETCH_IMAGE_STATS,
} from '@/store/action-types';


describe('Image Provider Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      expect(store.state.imageStats).toHaveLength(0);
      expect(store.state.isFetchingImageStatsError).toBeFalsy();
      expect(store.state.isFetchingImageStats).toBeFalsy();
    });
  });

  describe('mutations', () => {
    let state = null;

    beforeEach(() => {
      state = {};
    });

    it('FETCH_IMAGE_STATS_START sets isFetchingImageStats to true', () => {
      store.mutations[FETCH_IMAGE_STATS_START](state);

      expect(state.isFetchingImageStats).toBeTruthy();
    });

    it('FETCH_IMAGE_STATS_END sets isFetchingImageStats to false', () => {
      store.mutations[FETCH_IMAGE_STATS_END](state);

      expect(state.isFetchingImageStats).toBeFalsy();
    });

    it('SET_FETCH_IMAGES_ERROR sets isFetchingImageStatsError', () => {
      const params = {
        isFetchingImageStatsError: true,
      };
      store.mutations[SET_FETCH_IMAGES_ERROR](state, params);

      expect(state.isFetchingImageStatsError).toBe(params.isFetchingImageStatsError);
    });

    it('SET_IMAGE_STATS sets imageStats', () => {
      const params = {
        imageStats: true,
      };
      store.mutations[SET_IMAGE_STATS](state, params);

      expect(state.imageStats).toBe(params.imageStats);
    });
  });

  describe('actions', () => {
    const data = 'foobar';
    const imageProviderServiceMock = {
      getProviderStats: jest.fn(() => Promise.resolve({ data })),
    };
    const commit = jest.fn();
    it('FETCH_IMAGE_STATS on success', (done) => {
      const action = store.actions(imageProviderServiceMock)[FETCH_IMAGE_STATS];
      action({ commit }, {}).then(() => {
        expect(commit).toBeCalledWith(SET_FETCH_IMAGES_ERROR, { isFetchingImageStatsError: false });
        expect(commit).toBeCalledWith(FETCH_IMAGE_STATS_START);

        expect(imageProviderServiceMock.getProviderStats).toBeCalled();

        expect(commit).toBeCalledWith(FETCH_IMAGE_STATS_END);
        expect(commit).toBeCalledWith(SET_IMAGE_STATS, { imageStats: data });
        done();
      });
    });

    it('FETCH_IMAGE_STATS on failure', (done) => {
      const failedServiceMock = {
        getProviderStats: jest.fn(() => Promise.reject('error')),
      };
      const action = store.actions(failedServiceMock)[FETCH_IMAGE_STATS];
      action({ commit }, {}).catch(() => {
        expect(imageProviderServiceMock.getProviderStats).toBeCalled();
        expect(commit).toBeCalledWith(SET_FETCH_IMAGES_ERROR, { isFetchingImageStatsError: true });
        done();
      });
    });
  });
});
