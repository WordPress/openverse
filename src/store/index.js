import MediaProviderService from '~/data/media-provider-service'
import ImageService from '~/data/image-service'
import BugReportService from '~/data/bug-report-service'
import UsageDataService from '~/data/usage-data-service'
import ReportService from '~/data/report-service'
import SearchStore from '~/store-modules/search-store'
import MediaProviderStore from '~/store-modules/media-provider-store'
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
import { FETCH_MEDIA_PROVIDERS } from '~/store-modules/action-types'
import GoogleAnalytics from '~/analytics/google-analytics'
import { AUDIO, IMAGE } from '~/constants/media'

const AudioProviderService = MediaProviderService(AUDIO)
const ImageProviderService = MediaProviderService(IMAGE)

export const actions = Object.assign(
  UsageDataStore.actions(UsageDataService),
  SearchStore.actions(ImageService),
  FilterStore.actions,
  MediaProviderStore.actions(AudioProviderService, ImageProviderService),
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
        await dispatch(FETCH_MEDIA_PROVIDERS)
      } catch (error) {
        // TODO: What happens if we do not have image providers?
        // How do we show the error to the user?
        console.error("Couldn't fetch media providers")
      }
    },
  }
)

export const state = () =>
  Object.assign(
    SearchStore.state,
    FilterStore.state,
    MediaProviderStore.state,
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
  MediaProviderStore.mutations,
  BugReportStore.mutations,
  ABTestStore.mutations,
  ReportContentStore.mutations,
  RelatedImagesStore.mutations,
  NotificationStore.mutations,
  NavStore.mutations
)
