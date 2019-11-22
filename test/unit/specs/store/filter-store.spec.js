import { default as store, filterData} from '@/store/filter-store';
import { TOGGLE_FILTER } from '@/store/action-types';
import { SET_FILTER, SET_PROVIDERS_FILTERS, CLEAR_FILTERS } from '@/store/mutation-types';
import { notDeepEqual } from 'assert';

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
    const routePushMock = jest.fn();
    const mutations = store.mutations(routePushMock);

    beforeEach(() => {
      state = {
        query: { q: 'foo' },
        ...store.state(''),
      };
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
  });
});
