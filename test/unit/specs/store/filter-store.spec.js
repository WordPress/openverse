import store, { filterData } from '@/store/filter-store';
import { TOGGLE_FILTER } from '@/store/action-types';
import { SET_FILTER, SET_PROVIDERS_FILTERS, CLEAR_FILTERS } from '@/store/mutation-types';

describe('Filter Store', () => {
  describe('state', () => {
    it('state contains licenses', () => {
      const defaultState = store.state('');

      expect(defaultState.filters.licenses).toEqual(filterData.licenses);
    });

    it('state contains license types', () => {
      const defaultState = store.state('');

      expect(defaultState.filters.licenseTypes).toEqual(filterData.licenseTypes);
    });

    it('state contains image types', () => {
      const defaultState = store.state('');

      expect(defaultState.filters.imageTypes).toEqual(filterData.imageTypes);
    });

    it('state contains extensions', () => {
      const defaultState = store.state('');

      expect(defaultState.filters.extensions).toEqual(filterData.extensions);
    });

    it('state contains empty providers list', () => {
      const defaultState = store.state('');

      expect(defaultState.filters.providers).toEqual([]);
    });

    it('state contains search by author', () => {
      const defaultState = store.state('');

      expect(defaultState.filters.searchBy.author).toEqual(filterData.searchBy.author);
    });

    it('gets query from search params', () => {
      const state = store.state('?q=landscapes&provider=met&li=by&lt=commercial&searchBy=creator');
      expect(state.filters.providers.find(x => x.code === 'met').checked).toBeTruthy();
      expect(state.filters.licenses.find(x => x.code === 'by').checked).toBeTruthy();
      expect(state.filters.licenseTypes.find(x => x.code === 'commercial').checked).toBeTruthy();
      expect(state.filters.searchBy.creator).toBeTruthy();
    });
  });

  describe('mutations', () => {
    let state = null;
    let routePushMock = null;
    let mutations = null;

    beforeEach(() => {
      state = {
        query: { q: 'foo' },
        ...store.state(''),
      };
      routePushMock = jest.fn();
      mutations = store.mutations(routePushMock);
    });

    it('SET_FILTER updates license state', () => {
      mutations[SET_FILTER](state, { filterType: 'licenses', codeIdx: 0 });

      expect(state.filters.licenses[0].checked).toBeTruthy();
      expect(state.query).toEqual({
        q: 'foo',
        li: state.filters.licenses[0].code,
        extension: '',
        imageType: '',
        lt: '',
        provider: '',
        searchBy: '',
      });
    });

    it('SET_FILTER updates license type state', () => {
      mutations[SET_FILTER](state, { filterType: 'licenseTypes', codeIdx: 0 });

      expect(state.filters.licenseTypes[0].checked).toBeTruthy();
      expect(state.query).toEqual({
        q: 'foo',
        li: '',
        extension: '',
        imageType: '',
        lt: state.filters.licenseTypes[0].code,
        provider: '',
        searchBy: '',
      });
    });

    it('SET_FILTER updates extensions state', () => {
      mutations[SET_FILTER](state, { filterType: 'extensions', codeIdx: 0 });

      expect(state.filters.extensions[0].checked).toBeTruthy();
      expect(state.query).toEqual({
        q: 'foo',
        li: '',
        extension: state.filters.extensions[0].code,
        imageType: '',
        lt: '',
        provider: '',
        searchBy: '',
      });
    });

    it('SET_FILTER updates image types state', () => {
      mutations[SET_FILTER](state, { filterType: 'imageTypes', codeIdx: 0 });

      expect(state.filters.imageTypes[0].checked).toBeTruthy();
      expect(state.query).toEqual({
        q: 'foo',
        li: '',
        extension: '',
        imageType: state.filters.imageTypes[0].code,
        lt: '',
        provider: '',
        searchBy: '',
      });
    });

    it('SET_FILTER updates search by creator', () => {
      mutations[SET_FILTER](state, { filterType: 'searchBy' });

      expect(state.filters.searchBy.creator).toBeTruthy();
      expect(state.query).toEqual({
        q: 'foo',
        li: '',
        extension: '',
        imageType: '',
        lt: '',
        provider: '',
        searchBy: 'creator',
      });
    });

    it('SET_FILTER redirects to search path and with query object', () => {
      mutations[SET_FILTER](state, { filterType: 'imageTypes', codeIdx: 0, shouldNavigate: true });

      expect(routePushMock).toHaveBeenCalledWith({
        path: '/search',
        query: state.query,
      });
    });

    it('SET_FILTER redirects to collections path and with query object', () => {
      mutations[SET_FILTER](state, {
        filterType: 'imageTypes',
        codeIdx: 0,
        isCollectionsPage: true,
        provider: 'met',
        shouldNavigate: true,
      });

      expect(routePushMock).toHaveBeenCalledWith({
        path: '/collections/met',
        query: state.query,
      });
    });


    it('SET_PROVIDERS_FILTERS merges with existing provider filters', () => {
      const existingProviderFilters = [
        { code: 'met', checked: true },
      ];

      const providers = [
        { provider_name: 'met', display_name: 'Metropolitan' },
        { provider_name: 'flickr', display_name: 'Flickr' },
      ];

      state.filters.providers = existingProviderFilters;

      mutations[SET_PROVIDERS_FILTERS](state, { imageProviders: providers });

      expect(state.filters.providers).toEqual([
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ]);
    });

    it('CLEAR_FILTERS resets filters to initial state', () => {
      mutations[CLEAR_FILTERS](state, { shouldNavigate: false });

      expect(state.filters).toEqual(store.state('').filters);
    });

    it('CLEAR_FILTERS sets providers filters checked to false', () => {
      state.filters.providers = [
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ];

      mutations[CLEAR_FILTERS](state, { shouldNavigate: false });

      expect(state.filters.providers).toEqual([
        { code: 'met', name: 'Metropolitan', checked: false },
        { code: 'flickr', name: 'Flickr', checked: false },
      ]);
    });
  });

  describe('actions', () => {
    let state = null;
    let commitMock = null;
    let actions = null;

    beforeEach(() => {
      state = {
        query: { q: 'foo' },
        ...store.state(''),
      };
      commitMock = jest.fn();
      actions = store.actions;
    });

    it('TOGGLE_FILTER commits SET_FILTER with filter index', () => {
      state.filters.providers = [
        { code: 'met', name: 'Metropolitan', checked: true },
        { code: 'flickr', name: 'Flickr', checked: false },
      ];

      const params = { filterType: 'providers', code: 'flickr' };

      actions[TOGGLE_FILTER]({ commit: commitMock, state }, params);

      expect(commitMock).toHaveBeenCalledWith(SET_FILTER, {
        codeIdx: 1,
        ...params,
      });
    });
  });
});

