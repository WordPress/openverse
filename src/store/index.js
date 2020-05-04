import Vue from 'vue';
import Vuex from 'vuex';
import redirectTo from '@/router/redirectTo';
import ImageProviderService from '@/api/ImageProviderService';
import ImageService from '@/api/ImageService';
import BugReportService from '@/api/BugReportService';
import UsageDataService from '@/api/UsageDataService';
import ReportService from '@/api/ReportService';
import SearchStore from './search-store';
import ImageProviderStore from './image-provider-store';
import AttributionStore from './attribution-store';
import BugReportStore from './bug-report-store';
import SocialMediaStore from './social-store';
import ABTestStore from './abtest-store';
import UserStore from './user-store';
import UsageDataStore from './usage-data-store';
import FilterStore from './filter-store';
import ReportContentStore from './report-content-store';

Vue.use(Vuex);

const queryParams = !(typeof window === 'undefined') ? window.location.search : '';

const store = (GoogleAnalytics, router) => (new Vuex.Store({
  actions: Object.assign(
    UsageDataStore.actions(UsageDataService),
    SearchStore.actions(ImageService),
    FilterStore.actions,
    ImageProviderStore.actions(ImageProviderService),
    AttributionStore.actions(GoogleAnalytics),
    BugReportStore.actions(BugReportService),
    SocialMediaStore.actions(GoogleAnalytics),
    ABTestStore.actions,
    ReportContentStore.actions(ReportService),
  ),
  state: Object.assign(
    SearchStore.state(queryParams),
    FilterStore.state(queryParams),
    ImageProviderStore.state,
    BugReportStore.state,
    ABTestStore.state,
    UserStore.state,
    ReportContentStore.state,
  ),
  mutations: Object.assign(
    SearchStore.mutations(redirectTo(router)),
    FilterStore.mutations(redirectTo(router)),
    ImageProviderStore.mutations,
    BugReportStore.mutations,
    ABTestStore.mutations,
    ReportContentStore.mutations,
  ),
}));

export default store;
