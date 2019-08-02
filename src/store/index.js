import Vue from 'vue';
import Vuex from 'vuex';
import redirectTo from '@/router/redirectTo';
import ImageProviderService from '@/api/ImageProviderService';
import ImageService from '@/api/ImageService';
import BugReportService from '@/api/BugReportService';
import SearchStore from './search-store';
import ImageProviderStore from './image-provider-store';
import AttributionStore from './attribution-store';
import BugReportStore from './bug-report-store';
import SocialMediaStore from './social-store';
import ABTestStore from './abtest-store';

Vue.use(Vuex);

const queryParams = !(typeof window === 'undefined') ? window.location.search : '';

const store = (GoogleAnalytics, router) => (new Vuex.Store({
  actions: Object.assign(
    SearchStore.actions(ImageService),
    ImageProviderStore.actions(ImageProviderService),
    AttributionStore.actions(GoogleAnalytics),
    BugReportStore.actions(BugReportService),
    SocialMediaStore.actions(GoogleAnalytics),
  ),
  state: Object.assign(
    SearchStore.state(queryParams),
    ImageProviderStore.state,
    BugReportStore.state,
    ABTestStore.state,
  ),
  mutations: Object.assign(
    SearchStore.mutations(redirectTo(router)),
    ImageProviderStore.mutations,
    BugReportStore.mutations,
    ABTestStore.mutations,
  ),
}));

export default store;
