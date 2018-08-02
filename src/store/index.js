import Puex from 'puex';
import Vue from 'vue';
import SearchStore from './search-store';

Vue.use(Puex);

const store = new Puex({
  actions: SearchStore.actions,
  state: SearchStore.state,
  mutations: SearchStore.mutations,
});

export default store;
