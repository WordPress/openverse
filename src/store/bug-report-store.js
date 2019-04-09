import {
  REPORT_BUG,
} from './action-types';

const actions = bugReportService => ({
  // eslint-disable-next-line no-unused-vars
  [REPORT_BUG]({ commit }, params) {
    bugReportService.reportBug(params);
  },
});

export default {
  actions,
};
