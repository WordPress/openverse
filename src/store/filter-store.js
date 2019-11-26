import findIndex from 'lodash.findindex';
import clonedeep from 'lodash.clonedeep';
import getParameterByName from '@/utils/getParameterByName';
import { TOGGLE_FILTER } from './action-types';
import { SET_FILTER, SET_PROVIDERS_FILTERS, CLEAR_FILTERS, SET_FILTER_IS_VISIBLE } from './mutation-types';
import filterToQueryData from '../utils/filterToQueryData';

export const filterData = {
  licenses: [
    { code: 'cc0', name: 'CC0', checked: false },
    { code: 'pdm', name: 'Public Domain Mark', checked: false },
    { code: 'by', name: 'BY', checked: false },
    { code: 'by-sa', name: 'BY-SA', checked: false },
    { code: 'by-nc', name: 'BY-NC', checked: false },
    { code: 'by-nd', name: 'BY-ND', checked: false },
    { code: 'by-nc-sa', name: 'BY-NC-SA', checked: false },
    { code: 'by-nc-nd', name: 'BY-NC-ND', checked: false },
  ],
  licenseTypes: [
    { code: 'commercial', name: 'Use for commercial purposes', checked: false },
    { code: 'modification', name: 'Modify or adapt', checked: false },
  ],
  imageTypes: [
    { code: 'photo', name: 'Photographs', checked: false },
    { code: 'illustration', name: 'Illustrations', checked: false },
    { code: 'vector', name: 'Vector Graphics', checked: false },
  ],
  extensions: [
    { code: 'jpg', name: 'JPEGs', checked: false },
    { code: 'png', name: 'PNGs', checked: false },
    { code: 'gif', name: 'GIFs', checked: false },
    { code: 'svg', name: 'SVGs', checked: false },
  ],
  providers: [],
  searchBy: {
    creator: false,
  },
};

const parseQueryString = (queryString, queryStringParamKey, filterKey, data) => {
  const queryStringFilters = getParameterByName(queryStringParamKey, queryString).split(',');
  data[filterKey].forEach((filter) => {
    if (findIndex(queryStringFilters, f => f === filter.code) >= 0) {
      // eslint-disable-next-line no-param-reassign
      filter.checked = true;
    }
  });
};

const initialState = (searchParams) => {
  const filters = clonedeep(filterData);
  const providerParameter = getParameterByName('provider', searchParams);
  filters.providers = providerParameter === '' ? [] : providerParameter.split(',').map(provider => ({
    code: provider,
    checked: true,
  }));
  parseQueryString(searchParams, 'lt', 'licenseTypes', filters);
  parseQueryString(searchParams, 'li', 'licenses', filters);
  parseQueryString(searchParams, 'imageType', 'imageTypes', filters);
  parseQueryString(searchParams, 'extension', 'extensions', filters);

  const searchBy = getParameterByName('searchBy', searchParams);
  if (searchBy === 'creator') {
    filters.searchBy.creator = true;
  }

  const isFilterVisible = true;
  const isFilterApplied = !!filters.providers ||
                          !!filters.licenseTypes ||
                          !!filters.searchBy.creator;
  return {
    filters,
    isFilterVisible,
    isFilterApplied,
  };
};

const actions = {
  [TOGGLE_FILTER]({ commit, state }, params) {
    const filters = state.filters[params.filterType];
    const codeIdx = findIndex(filters, f => f.code === params.code);

    commit(SET_FILTER, {
      codeIdx,
      ...params,
    });
  },
};

function setQuery(state, params, path, redirect) {
  const query = filterToQueryData(state.filters);
  state.isFilterApplied = ['providers', 'lt', 'li', 'imageType', 'extension', 'searchBy']
    .some(key => query[key] && query[key].length > 0);
  state.query = {
    q: state.query.q,
    ...query,
  };
  if (params.shouldNavigate === true) {
    redirect({ path, query: state.query });
  }
}

function setFilter(state, params, path, redirect) {
  if (params.filterType === 'searchBy') {
    state.filters.searchBy.creator = !state.filters.searchBy.creator;
  }
  else {
    const filters = state.filters[params.filterType];
    filters[params.codeIdx].checked = !filters[params.codeIdx].checked;
  }

  setQuery(state, params, path, redirect);
}

const redirectUrl = params => (params.isCollectionsPage ? `/collections/${params.provider}` : '/search');

const mutations = redirect => ({
  [SET_FILTER](state, params) {
    return setFilter(state, params, redirectUrl(params), redirect);
  },
  [CLEAR_FILTERS](state, params) {
    const initialFilters = initialState('').filters;
    const resetProviders = state.filters.providers.map(provider => ({
      ...provider,
      checked: false,
    }));
    state.filters = {
      ...initialFilters,
      providers: resetProviders,
    };
    return setQuery(state, params, redirectUrl(params), redirect);
  },
  [SET_PROVIDERS_FILTERS](state, params) {
    const providers = params.imageProviders;
    // merge providers from API response with the filters that came from the
    // browse URL search query string and match the checked properties
    // in the store
    state.filters.providers = providers.map((provider) => {
      const existingProviderFilterIdx = findIndex(
        state.filters.providers,
        p => p.code === provider.provider_name);

      const checked = existingProviderFilterIdx >= 0 ?
        state.filters.providers[existingProviderFilterIdx].checked :
        false;

      return {
        code: provider.provider_name,
        name: provider.display_name,
        checked,
      };
    });
  },
  [SET_FILTER_IS_VISIBLE](state, params) {
    state.isFilterVisible = params.isFilterVisible;
  },
});

export default {
  state: initialState,
  actions,
  mutations,
};

