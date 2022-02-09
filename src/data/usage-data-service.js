import { createApiService } from './api-service'

const baseUrl = process.env.apiUrl

// Analytics API is available at `http://api.openverse.engineering/analytics/`
// and not `http://api.openverse.engineering/v1/analytics
const ApiService = createApiService(baseUrl?.replace('/v1', ''))

/** @typedef {'search_event' | 'result_click_event' | 'detail_page_event' | 'search_rating_event'} SearchEventName */

const UsageDataService = {
  /**
   * @param {SearchEventName} endpoint
   * @param {Parameters<typeof ApiService['post']>[1]} data
   */
  post(endpoint, data) {
    return ApiService.post(`analytics/${endpoint}/`, data)
  },

  /**
   * @param {object} props
   * @param {string} props.query
   * @param {string} props.sessionId
   */
  sendSearchQueryEvent({ query, sessionId }) {
    return this.post('search_event', { query, session_uuid: sessionId })
  },

  /**
   * @param {object} props
   * @param {string} props.query
   * @param {unknown} props.resultRank
   * @param {string} props.resultUuid
   * @param {string} props.sessionId
   */
  sendResultClickedEvent({ query, resultRank, resultUuid, sessionId }) {
    return this.post('result_click_event', {
      query,
      result_rank: resultRank,
      result_uuid: resultUuid,
      session_uuid: sessionId,
    })
  },

  /**
   * @param {object} props
   * @param {string} props.eventType
   * @param {string} props.resultUuid
   */
  sendDetailPageEvent({ eventType, resultUuid }) {
    return this.post('detail_page_event', {
      event_type: eventType,
      result_uuid: resultUuid,
    })
  },

  /**
   * @param {object} props
   * @param {string} props.query
   * @param {boolean} props.relevant
   */
  sendSearchRatingEvent({ query, relevant }) {
    return this.post('search_rating_event', { query, relevant })
  },
}

export default UsageDataService
