import Puex from 'puex';
import Vue from 'vue';
import { routePush } from '@/router';
import ImageProviderService from '@/api/ImageProviderService';
import ImageService from '@/api/ImageService';
import GoogleAnalytics from '@/analytics/GoogleAnalytics';
import SearchStore from './search-store';
import ListStore from './share-list-store';
import ImageProviderStore from './image-provider-store';
import AttributionStore from './attribution-store';

Vue.use(Puex);

const store = new Puex({
  actions: Object.assign(
    SearchStore.actions(ImageService),
    ListStore.actions,
    ImageProviderStore.actions(ImageProviderService),
    AttributionStore.actions(GoogleAnalytics),
  ),
  state: Object.assign(
    SearchStore.state(window.location.search),
    ListStore.state,
    ImageProviderStore.state,
  ),
  mutations: Object.assign(
    SearchStore.mutations(routePush),
    ListStore.mutations,
    ImageProviderStore.mutations,
  ),
});

export default store;
