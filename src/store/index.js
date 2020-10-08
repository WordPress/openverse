import ImageProviderService from '~/data/ImageProviderService'
import ImageService from '~/data/ImageService'
import BugReportService from '~/data/BugReportService'
import UsageDataService from '~/data/UsageDataService'
import ReportService from '~/data/ReportService'
import SearchStore from '~/store-modules/search-store'
import ImageProviderStore from '~/store-modules/image-provider-store'
import AttributionStore from '~/store-modules/attribution-store'
import BugReportStore from '~/store-modules/bug-report-store'
import SocialMediaStore from '~/store-modules/social-store'
import ABTestStore from '~/store-modules/abtest-store'
import UserStore from '~/store-modules/user-store'
import UsageDataStore from '~/store-modules/usage-data-store'
import FilterStore from '~/store-modules/filter-store'
import ReportContentStore from '~/store-modules/report-content-store'
import RelatedImagesStore from '~/store-modules/related-images-store'
import { FETCH_IMAGE_PROVIDERS } from '~/store-modules/action-types'
import GoogleAnalytics from '~/analytics/GoogleAnalytics'

/**
 * Runs once on the server-side per user session. Useful for global things that need to fire once.
 * View the Nuxt docs {@link https://nuxtjs.org/guide/vuex-store#the-nuxtserverinit-action} for more info.
 * @param {import('vuex').ActionContext} VuexContext
 * @param {import('@nuxt/types').Context} NuxtContext
 */
async function nuxtServerInit({ dispatch }, { req }) {
  // Here we can access cookie info server-side!
  console.info(req.headers.cookie)
  await dispatch(FETCH_IMAGE_PROVIDERS)
}

export const actions = Object.assign(
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
  { nuxtServerInit }
)

export const state = () =>
  Object.assign(
    SearchStore.state,
    FilterStore.state,
    ImageProviderStore.state,
    BugReportStore.state,
    ABTestStore.state,
    UserStore.state,
    ReportContentStore.state,
    RelatedImagesStore.state
  )

export const mutations = Object.assign(
  SearchStore.mutations,
  FilterStore.mutations,
  ImageProviderStore.mutations,
  BugReportStore.mutations,
  ABTestStore.mutations,
  ReportContentStore.mutations,
  RelatedImagesStore.mutations
)
