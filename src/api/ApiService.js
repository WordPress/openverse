
import Vue from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';
import es6Promise from 'es6-promise';

es6Promise.polyfill();

const BASE_URL = 'http://api-dev.creativecommons.engineering';


const ApiService = {
  init(baseUrl = BASE_URL, authParams) {
    Vue.use(VueAxios, axios);
    Vue.axios.defaults.baseURL = baseUrl;
    Vue.axios.defaults.auth = authParams;
  },

  setHeader(headerParams) {
    Object.assign(Vue.axios.defaults.headers, headerParams);
  },

  query(resource, params) {
    return Vue.axios
      .get(resource, { params })
      .catch((error) => {
        throw new Error(`[RWV] ApiService ${error}`);
      });
  },

  get(resource, slug = '') {
    return Vue.axios
      .get(`${resource}/${slug}`)
      .catch((error) => {
        throw new Error(`[RWV] ApiService ${error}`);
      });
  },

  post(resource, params) {
    return Vue.axios.post(`${resource}`, params);
  },

  update(resource, slug, params) {
    return Vue.axios.put(`${resource}/${slug}`, params);
  },

  put(resource, params) {
    return Vue.axios.put(`${resource}`, params);
  },

  delete(resource) {
    return Vue.axios
      .delete(resource)
      .catch((error) => {
        throw new Error(`[RWV] ApiService ${error}`);
      });
  },
};

export default ApiService;
