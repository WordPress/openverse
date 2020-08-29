import {
  SEND_SEARCH_QUERY_EVENT,
  SEND_RESULT_CLICKED_EVENT,
  SEND_DETAIL_PAGE_EVENT,
  SEND_SEARCH_RATING_EVENT,
} from './usage-data-analytics-types'

const actions = (UsageDataService) => ({
  [SEND_SEARCH_QUERY_EVENT](context, params) {
    if (process.env.disableApiAnalytics) return
    UsageDataService.sendSearchQueryEvent(params)
  },
  [SEND_RESULT_CLICKED_EVENT](context, params) {
    if (process.env.disableApiAnalytics) return
    UsageDataService.sendResultClickedEvent(params)
  },
  [SEND_SEARCH_RATING_EVENT](context, params) {
    if (process.env.disableApiAnalytics) return
    UsageDataService.sendSearchRatingEvent(params)
  },
  [SEND_DETAIL_PAGE_EVENT](context, params) {
    if (process.env.disableApiAnalytics) return
    UsageDataService.sendDetailPageEvent(params)
  },
})

export default {
  actions,
}
