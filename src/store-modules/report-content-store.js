import {
  TOGGLE_REPORT_FORM_VISIBILITY,
  REPORT_SENT,
  REPORT_FORM_CLOSED,
  REPORT_ERROR,
  BACK_TO_REPORT_START,
} from './mutation-types'
import { SEND_CONTENT_REPORT } from './action-types'

const state = {
  isReportFormVisible: false,
  isReportSent: false,
  reportFailed: false,
}

/* eslint no-param-reassign: ["error", { "props": false }] */
const mutations = {
  [TOGGLE_REPORT_FORM_VISIBILITY](_state) {
    _state.isReportFormVisible = !_state.isReportFormVisible
  },
  [REPORT_SENT](_state) {
    _state.isReportSent = true
  },
  [REPORT_ERROR](_state) {
    _state.reportFailed = true
  },
  [BACK_TO_REPORT_START](_state) {
    _state.reportFailed = false
    _state.isReportSent = false
  },
  [REPORT_FORM_CLOSED](_state) {
    _state.isReportSent = false
    _state.reportFailed = false
    _state.isReportFormVisible = false
  },
}

const actions = (ReportService) => ({
  [SEND_CONTENT_REPORT]({ commit }, params) {
    return ReportService.sendReport(params)
      .then(() => commit(REPORT_SENT))
      .catch(() => commit(REPORT_ERROR))
  },
})

export default {
  state,
  mutations,
  actions,
}
