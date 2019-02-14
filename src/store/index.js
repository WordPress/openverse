import Puex from 'puex';
import Vue from 'vue';
import { routePush } from '@/router';
import ImageProviderService from '@/api/ImageProviderService';
import ImageService from '@/api/ImageService';
import SearchStore from './search-store';
import ListStore from './share-list-store';
import ImageProviderStore from './image-provider-store';

Vue.use(Puex);

const store = new Puex({
  actions: Object.assign(
    SearchStore.actions(ImageService),
    ListStore.actions,
    ImageProviderStore.actions(ImageProviderService),
  ),
  state: Object.assign(
    SearchStore.state,
    ListStore.state,
    ImageProviderStore.state,
  ),
  mutations: Object.assign(
    SearchStore.mutations(routePush),
    ListStore.mutations,
    ImageProviderStore.mutations,
  ),
});

export const commit = (action, params) => store.commit(action, params);

export default store;
