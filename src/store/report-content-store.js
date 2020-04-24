import { TOGGLE_REPORT_FORM_VISIBILITY, REPORT_SENT, REPORT_FORM_CLOSED } from './mutation-types';
import { SEND_CONTENT_REPORT } from './action-types';

const state = {
  isReportFormVisible: false,
  isReportSent: false,
};

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [TOGGLE_REPORT_FORM_VISIBILITY](_state) {
    _state.isReportFormVisible = !_state.isReportFormVisible;
  },
  [REPORT_SENT](_state) {
    _state.isReportSent = true;
  },
  [REPORT_FORM_CLOSED](_state) {
    _state.isReportSent = false;
    _state.isReportFormVisible = false;
  },
};


const actions = ReportService => ({
  [SEND_CONTENT_REPORT]({ commit }, params) {
    ReportService.sendReport(params)
      .then(() => commit(REPORT_SENT))
      .catch(() => commit(REPORT_SENT));
  },
});

export default {
  state,
  mutations,
  actions,
};
