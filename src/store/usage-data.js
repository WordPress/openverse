import {
  SEND_SEARCH_QUERY_EVENT,
  SEND_RESULT_CLICKED_EVENT,
  SEND_DETAIL_PAGE_EVENT,
  SEND_SEARCH_RATING_EVENT,
} from '~/constants/usage-data-analytics-types'
import stringToBoolean from '~/utils/string-to-boolean'
import UsageDataService from '~/data/usage-data-service'
import { sentry as sentryConfig } from '~/utils/sentry-config'

const disabled = !stringToBoolean(process.env.enableInternalAnalytics)

/**
 * Catch api event failures, mainly to prevent SSR errors on test domains that cannot communicate with our API server.
 * Alternatively, just disable internal analytics on those servers with ENABLE_INTERNAL_ANALYTICS=true in the environment.
 * @param {string} eventName
 * @param {import('vue').default} context
 */
const handleUsageEvent = (eventName, context) => (promise) =>
  promise.catch(
    (error) =>
      // $sentryReady won't exist if sentry has been disabled
      !sentryConfig.disabled &&
      context.$sentryReady().then((sentry) =>
        sentry.captureException(error, (scope) => {
          scope.setTag('event_name', eventName)
          scope.setTag('request_url', error.config.url)
        })
      )
  )

/**
 *
 * @param {typeof UsageDataService} usageDataService
 */
export const createActions = (usageDataService) => ({
  [SEND_SEARCH_QUERY_EVENT](context, params) {
    if (disabled) return
    handleUsageEvent(
      SEND_SEARCH_QUERY_EVENT,
      this
    )(usageDataService.sendSearchQueryEvent(params))
  },
  async [SEND_RESULT_CLICKED_EVENT](context, params) {
    if (disabled) return
    handleUsageEvent(
      SEND_RESULT_CLICKED_EVENT,
      this
    )(usageDataService.sendResultClickedEvent(params))
  },
  [SEND_SEARCH_RATING_EVENT](context, params) {
    if (disabled) return
    handleUsageEvent(
      SEND_SEARCH_RATING_EVENT,
      this
    )(usageDataService.sendSearchRatingEvent(params))
  },
  [SEND_DETAIL_PAGE_EVENT](context, params) {
    if (disabled) return
    handleUsageEvent(
      SEND_DETAIL_PAGE_EVENT,
      this
    )(usageDataService.sendDetailPageEvent(params))
  },
})

export const actions = createActions(UsageDataService)
