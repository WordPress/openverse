import {
  SEND_SEARCH_QUERY_EVENT,
  SEND_RESULT_CLICKED_EVENT,
  SEND_DETAIL_PAGE_EVENT,
  SEND_SEARCH_RATING_EVENT,
} from './usage-data-analytics-types'
import stringToBoolean from '~/utils/stringToBoolean'

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

const actions = (UsageDataService) => ({
  [SEND_SEARCH_QUERY_EVENT](context, params) {
    if (disabled) return
    handleUsageEvent(SEND_SEARCH_QUERY_EVENT)(
      UsageDataService.sendSearchQueryEvent(params)
    )
  },
  [SEND_RESULT_CLICKED_EVENT](context, params) {
    if (disabled) return
    handleUsageEvent(SEND_RESULT_CLICKED_EVENT)(
      UsageDataService.sendResultClickedEvent(params)
    )
  },
  [SEND_SEARCH_RATING_EVENT](context, params) {
    if (disabled) return
    handleUsageEvent(SEND_SEARCH_RATING_EVENT)(
      UsageDataService.sendSearchRatingEvent(params)
    )
  },
  [SEND_DETAIL_PAGE_EVENT](context, params) {
    if (disabled) return
    handleUsageEvent(SEND_DETAIL_PAGE_EVENT)(
      UsageDataService.sendDetailPageEvent(params)
    )
  },
})

export default { actions }
