import AudioService from '~/data/audio-service'
import ImageService from '~/data/image-service'
import UsageDataService from '~/data/usage-data-service'
import ReportService from '~/data/report-service'
import SearchStore from '~/store-modules/search-store'
import SocialMediaStore from '~/store-modules/social-store'
import UserStore from '~/store-modules/user-store'
import UsageDataStore from '~/store-modules/usage-data-store'
import FilterStore from '~/store-modules/filter-store'
import ReportContentStore from '~/store-modules/report-content-store'
import NotificationStore from '~/store-modules/notification-store'
import { FETCH_MEDIA_PROVIDERS } from '~/constants/action-types'
import GoogleAnalytics from '~/analytics/google-analytics'
import { PROVIDER } from '~/constants/store-modules'

export const actions = Object.assign(
  UsageDataStore.actions(UsageDataService),
  SearchStore.actions(AudioService, ImageService),
  FilterStore.actions,
  SocialMediaStore.actions(GoogleAnalytics),
  ReportContentStore.actions(ReportService),
  NotificationStore.actions,
  {
    async nuxtServerInit({ dispatch }) {
      try {
        await dispatch(`${PROVIDER}/${FETCH_MEDIA_PROVIDERS}`)
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
    UserStore.state,
    ReportContentStore.state,
    NotificationStore.state
  )

export const getters = Object.assign(FilterStore.getters)

export const mutations = Object.assign(
  SearchStore.mutations,
  FilterStore.mutations,
  ReportContentStore.mutations,
  NotificationStore.mutations
)
