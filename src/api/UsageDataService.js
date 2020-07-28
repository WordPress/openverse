import { createApiService } from './ApiService'

const baseUrl = process.env.API_URL
// Analytics API is available at `http://api.creativecommons.engineering/analytics/`
// and not `http://api.creativecommons.engineering/v1/analytics
const ApiService = createApiService(baseUrl.replace('/v1', ''))

const UsageDataService = {
  post(endpoint, params) {
    return ApiService.post(`/analytics/${endpoint}`, params)
  },

  sendSearchQueryEvent({ query, sessionId }) {
    return this.post('search_event', { query, session_uuid: sessionId })
  },

  sendResultClickedEvent({ query, resultRank, resultUuid, sessionId }) {
    return this.post('result_click_event', {
      query,
      result_rank: resultRank,
      result_uuid: resultUuid,
      session_uuid: sessionId,
    })
  },

  sendDetailPageEvent({ eventType, resultUuid }) {
    return this.post('detail_page_event', {
      event_type: eventType,
      result_uuid: resultUuid,
    })
  },

  sendSearchRatingEvent({ query, relevant }) {
    return this.post('search_rating_event', { query, relevant })
  },
}

export default UsageDataService
