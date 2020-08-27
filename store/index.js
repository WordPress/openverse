import Vuex from 'vuex'
import redirectTo from '../src/router/redirectTo'
import ImageProviderService from '../src/api/ImageProviderService'
import ImageService from '../src/api/ImageService'
import BugReportService from '../src/api/BugReportService'
import UsageDataService from '../src/api/UsageDataService'
import ReportService from '../src/api/ReportService'
import SearchStore from '../src/store/search-store'
import ImageProviderStore from '../src/store/image-provider-store'
import AttributionStore from '../src/store/attribution-store'
import BugReportStore from '../src/store/bug-report-store'
import SocialMediaStore from '../src/store/social-store'
import ABTestStore from '../src/store/abtest-store'
import UserStore from '../src/store/user-store'
import UsageDataStore from '../src/store/usage-data-store'
import FilterStore from '../src/store/filter-store'
import ReportContentStore from '../src/store/report-content-store'
import RelatedImagesStore from '../src/store/related-images-store'
import { FETCH_IMAGE_PROVIDERS } from '../src/store/action-types'

const queryParams = !(typeof window === 'undefined')
  ? window.location.search
  : ''

const store = (GoogleAnalytics, router) =>
  new Vuex.Store({
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
      RelatedImagesStore.actions(ImageService),
      {
        async nuxtServerInit({ dispatch }) {
          await dispatch(FETCH_IMAGE_PROVIDERS)
        },
      }
    ),
    state: Object.assign(
      SearchStore.state(queryParams),
      FilterStore.state(queryParams),
      ImageProviderStore.state,
      BugReportStore.state,
      ABTestStore.state,
      UserStore.state,
      ReportContentStore.state,
      RelatedImagesStore.state
    ),
    mutations: Object.assign(
      SearchStore.mutations(redirectTo(router)),
      FilterStore.mutations(redirectTo(router)),
      ImageProviderStore.mutations,
      BugReportStore.mutations,
      ABTestStore.mutations,
      ReportContentStore.mutations,
      RelatedImagesStore.mutations
    ),
  })

export default store
