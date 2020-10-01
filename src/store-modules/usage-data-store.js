import {
  SEND_SEARCH_QUERY_EVENT,
  SEND_RESULT_CLICKED_EVENT,
  SEND_DETAIL_PAGE_EVENT,
  SEND_SEARCH_RATING_EVENT,
} from './usage-data-analytics-types'
import stringToBoolean from '~/utils/stringToBoolean'

const actions = (UsageDataService) => ({
  [SEND_SEARCH_QUERY_EVENT](context, params) {
    if (stringToBoolean(process.env.apiAnalytics)) return
    UsageDataService.sendSearchQueryEvent(params)
  },
  [SEND_RESULT_CLICKED_EVENT](context, params) {
    if (stringToBoolean(process.env.apiAnalytics)) return
    UsageDataService.sendResultClickedEvent(params)
  },
  [SEND_SEARCH_RATING_EVENT](context, params) {
    if (stringToBoolean(process.env.apiAnalytics)) return
    UsageDataService.sendSearchRatingEvent(params)
  },
  [SEND_DETAIL_PAGE_EVENT](context, params) {
    if (stringToBoolean(process.env.apiAnalytics)) return
    UsageDataService.sendDetailPageEvent(params)
  },
})

export default {
  actions,
}
