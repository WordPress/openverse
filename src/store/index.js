import Puex from 'puex';
import Vue from 'vue';
import SearchStore from './search-store';
import ListStore from './share-list-store';
import ImageProviderStore from './image-provider-store';

Vue.use(Puex);

const store = new Puex({
  actions: Object.assign(
    SearchStore.actions,
    ListStore.actions,
    ImageProviderStore.actions,
  ),
  state: Object.assign(
    SearchStore.state,
    ListStore.state,
    ImageProviderStore.state,
  ),
  mutations: Object.assign(
    SearchStore.mutations,
    ListStore.mutations,
    ImageProviderStore.mutations,
  ),
});

export default store;
