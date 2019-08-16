import ApiService from './ApiService';

const UsageDataService = {
  post(endpoint, params) {
    return ApiService.post(`/analytics/${endpoint}`, params);
  },

  sendSearchQueryEvent({ query, sessionId }) {
    return this.post('search_event', { query, session_uuid: sessionId });
  },

  sendResultClickedEvent({ query, resultRank, resultUuid, sessionId }) {
    return this.post(
      'result_clicked_event',
      { query, result_rank: resultRank, result_uuid: resultUuid, session_uuid: sessionId },
    );
  },

  sendDetailPageEvent({ eventType, resultUuid }) {
    return this.post(
      'detail_page_event',
      { event_type: eventType, result_uuid: resultUuid },
    );
  },
};

export default UsageDataService;
