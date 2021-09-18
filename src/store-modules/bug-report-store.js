import { REPORT_BUG } from '../constants/action-types'

import {
  REPORT_BUG_START,
  REPORT_BUG_END,
  REPORT_BUG_FAILED,
} from '../constants/mutation-types'

const actions = (bugReportService) => ({
  // eslint-disable-next-line no-unused-vars
  [REPORT_BUG]({ commit }, params) {
    commit(REPORT_BUG_START)
    bugReportService
      .reportBug(params)
      .then(() => commit(REPORT_BUG_END))
      .catch(() => commit(REPORT_BUG_FAILED))
  },
})

const state = {
  isReportingBug: false,
  bugReported: false,
  bugReportFailed: false,
}

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [REPORT_BUG_START](_state) {
    _state.isReportingBug = true
  },
  [REPORT_BUG_END](_state) {
    _state.isReportingBug = false
    _state.bugReported = true
  },
  [REPORT_BUG_FAILED](_state) {
    _state.isReportingBug = false
    _state.bugReportFailed = true
  },
}

export default {
  actions,
  mutations,
  state,
}
