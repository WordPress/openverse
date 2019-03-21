import Puex from 'puex';
import Vue from 'vue';
import { routePush } from '@/router';
import ImageProviderService from '@/api/ImageProviderService';
import ImageService from '@/api/ImageService';
import SearchStore from './search-store';
import ImageProviderStore from './image-provider-store';
import AttributionStore from './attribution-store';

Vue.use(Puex);

const store = GoogleAnalytics => (new Puex({
  actions: Object.assign(
    SearchStore.actions(ImageService),
    ImageProviderStore.actions(ImageProviderService),
    AttributionStore.actions(GoogleAnalytics),
  ),
  state: Object.assign(
    SearchStore.state(window.location.search),
    ImageProviderStore.state,
  ),
  mutations: Object.assign(
    SearchStore.mutations(routePush),
    ImageProviderStore.mutations,
  ),
}));

export default store;
