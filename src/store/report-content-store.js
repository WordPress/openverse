import { TOGGLE_REPORT_FORM_VISIBILITY, REPORT_SENT } from './mutation-types';
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
};

const DCMA_FORM = 'https://docs.google.com/forms/d/e/1FAIpQLSdZLZpYJGegL8G2FsEAHNsR1nqVx1Wxfp-oj3o0h8rqe9j8dg/viewform';

const actions = ReportService => ({
  [SEND_CONTENT_REPORT]({ commit }, params) {
    if (params.reason === 'copyright') {
      window.open(DCMA_FORM);
    }
    else {
      ReportService.sendReport(params).then(() => commit(REPORT_SENT));
    }
  },
});

export default {
  state,
  mutations,
  actions,
};
