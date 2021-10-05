import {
  SEND_SEARCH_QUERY_EVENT,
  SEND_RESULT_CLICKED_EVENT,
  SEND_DETAIL_PAGE_EVENT,
  SEND_SEARCH_RATING_EVENT,
} from '~/constants/usage-data-analytics-types'
import stringToBoolean from '~/utils/string-to-boolean'
import UsageDataService from '~/data/usage-data-service'

const disabled = !stringToBoolean(process.env.enableInternalAnalytics)

/**
 * Catch api event failures, mainly to prevent SSR errors on test domains that cannot communicate with our API server.
 * Alternatively, just disable internal analytics on those servers with ENABLE_INTERNAL_ANALYTICS=true in the environment.
 */
const handleUsageEvent = (eventName) => (promise) =>
  promise.catch((error) =>
    console.error({
      message: `Failed to execute api event: ${eventName}.`,
      error,
    })
  )

export const createActions = (usageDataService) => ({
  async [SEND_SEARCH_QUERY_EVENT](context, params) {
    if (disabled) return
    await handleUsageEvent(SEND_SEARCH_QUERY_EVENT)(
      usageDataService.sendSearchQueryEvent(params)
    )
  },
  async [SEND_RESULT_CLICKED_EVENT](context, params) {
    if (disabled) return
    await handleUsageEvent(SEND_RESULT_CLICKED_EVENT)(
      usageDataService.sendResultClickedEvent(params)
    )
  },
  async [SEND_SEARCH_RATING_EVENT](context, params) {
    if (disabled) return
    await handleUsageEvent(SEND_SEARCH_RATING_EVENT)(
      usageDataService.sendSearchRatingEvent(params)
    )
  },
  async [SEND_DETAIL_PAGE_EVENT](context, params) {
    if (disabled) return
    await handleUsageEvent(SEND_DETAIL_PAGE_EVENT)(
      usageDataService.sendDetailPageEvent(params)
    )
  },
})

export const actions = createActions(UsageDataService)
