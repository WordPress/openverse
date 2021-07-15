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
import NotificationStore from '~/store-modules/notification-store'
import NavStore from '~/store-modules/nav-store'
import { FETCH_IMAGE_PROVIDERS } from '~/store-modules/action-types'
import GoogleAnalytics from '~/analytics/GoogleAnalytics'

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
  NotificationStore.actions,
  {
    async nuxtServerInit({ dispatch }) {
      try {
        await dispatch(FETCH_IMAGE_PROVIDERS)
      } catch (error) {
        // TODO: What happens if we do not have image providers?
        // How do we show the error to the user?
        console.error("Couldn't fetch image providers")
      }
    },
  }
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
    RelatedImagesStore.state,
    NotificationStore.state,
    NavStore.state
  )

export const getters = Object.assign(FilterStore.getters)

export const mutations = Object.assign(
  SearchStore.mutations,
  FilterStore.mutations,
  ImageProviderStore.mutations,
  BugReportStore.mutations,
  ABTestStore.mutations,
  ReportContentStore.mutations,
  RelatedImagesStore.mutations,
  NotificationStore.mutations,
  NavStore.mutations
)
