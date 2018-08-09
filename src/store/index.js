import Puex from 'puex';
import Vue from 'vue';
import SearchStore from './search-store';
import ListStore from './share-list-store';

Vue.use(Puex);

const store = new Puex({
  actions: Object.assign(SearchStore.actions, ListStore.actions),
  state: Object.assign(SearchStore.state, ListStore.state),
  mutations: Object.assign(SearchStore.mutations, ListStore.mutations),
});

export default store;
