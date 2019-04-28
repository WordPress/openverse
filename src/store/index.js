import Vue from 'vue';
import Vuex from 'vuex';
import { routePush } from '@/router';
import ImageProviderService from '@/api/ImageProviderService';
import ImageService from '@/api/ImageService';
import BugReportService from '@/api/BugReportService';
import SearchStore from './search-store';
import ImageProviderStore from './image-provider-store';
import AttributionStore from './attribution-store';
import BugReportStore from './bug-report-store';

Vue.use(Vuex);

const store = GoogleAnalytics => (new Vuex.Store({
  actions: Object.assign(
    SearchStore.actions(ImageService),
    ImageProviderStore.actions(ImageProviderService),
    AttributionStore.actions(GoogleAnalytics),
    BugReportStore.actions(BugReportService),
  ),
  state: Object.assign(
    SearchStore.state(window.location.search),
    ImageProviderStore.state,
    BugReportStore.state,
  ),
  mutations: Object.assign(
    SearchStore.mutations(routePush),
    ImageProviderStore.mutations,
    BugReportStore.mutations,
  ),
}));

export default store;
