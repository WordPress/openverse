import findIndex from 'lodash.findindex';
import clonedeep from 'lodash.clonedeep';
import getParameterByName from '@/utils/getParameterByName';
import { TOGGLE_FILTER } from './action-types';
import { SET_FILTER, SET_PROVIDERS_FILTERS } from './mutation-types';
import filterToQueryData from '../utils/filterToQueryData';

const filterData = {
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
    { code: 'photo', name: 'Photographs' },
    { code: 'illustration', name: 'Illustrations' },
    { code: 'vector', name: 'Vector Graphics' },
  ],
  extensions: [
    { code: 'jpg', name: 'JPEGs' },
    { code: 'png', name: 'PNGs' },
  ],
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
  filters.providers = getParameterByName('provider', searchParams).split(',').map(provider => ({
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

  filters.isFilterVisible = true;
  filters.isFilterApplied = !!filters.providers ||
                            !!filters.licenseTypes ||
                            !!filters.searchBy.creator;
  return {
    filters,
  };
};

const actions = {
  [TOGGLE_FILTER]({ commit, state }, params) {
    const filters = state.filters[params.filterType];
    const codeIdx = findIndex(filters, f => f.code === params.code);
    const shouldNavigate = params.shouldNavigate;

    commit(SET_FILTER, {
      filterType: params.filterType,
      codeIdx,
      shouldNavigate,
    });
  },
};

function setFilter(state, params, path, redirect) {
  const filters = state.filters[params.filterType];
  filters[params.codeIdx].checked = !filters[params.codeIdx].checked;
  const query = filterToQueryData(state.filters);
  state.isFilterApplied = ['providers', 'lt', 'imageType', 'extension', 'searchBy']
    .some(key => query[key] && query[key].length > 0);
  state.query = {
    q: state.query.q,
    ...query,
  };
  if (params.shouldNavigate === true) {
    redirect({ path, query: state.query });
  }
}

const mutations = redirect => ({
  [SET_FILTER](state, params) {
    return setFilter(state, params, '/search', redirect);
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
});

export default {
  state: initialState,
  actions,
  mutations,
};
