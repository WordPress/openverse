import store from '~/store-modules/report-content-store'
import {
  TOGGLE_REPORT_FORM_VISIBILITY,
  REPORT_SENT,
  REPORT_FORM_CLOSED,
  REPORT_ERROR,
  BACK_TO_REPORT_START,
} from '~/store-modules/mutation-types'
import { SEND_CONTENT_REPORT } from '~/store-modules/action-types'

describe('Report Content Store', () => {
  describe('state', () => {
    it('exports default state', () => {
      const state = store.state
      expect(state.isReportFormVisible).toBeFalsy()
      expect(state.isReportSent).toBeFalsy()
      expect(state.reportFailed).toBeFalsy()
    })
  })

  describe('mutations', () => {
    const mutations = store.mutations
    let state = null

    beforeEach(() => {
      state = {}
    })

    it('TOGGLE_REPORT_FORM_VISIBILITY toggles isReportFormVisible', () => {
      mutations[TOGGLE_REPORT_FORM_VISIBILITY](state)

      expect(state.isReportFormVisible).toBeTruthy()

      mutations[TOGGLE_REPORT_FORM_VISIBILITY](state)
      expect(state.isReportFormVisible).toBeFalsy()
    })

    it('REPORT_SENT sets isReportSent to true', () => {
      mutations[REPORT_SENT](state)

      expect(state.isReportSent).toBeTruthy()
    })

    it('REPORT_ERROR sets reportFailed to true', () => {
      mutations[REPORT_ERROR](state)

      expect(state.reportFailed).toBeTruthy()
    })

    it('BACK_TO_REPORT_START resets reportSent and Failed state', () => {
      state.isReportSent = true
      state.reportFailed = true
      mutations[BACK_TO_REPORT_START](state)

      expect(state.isReportSent).toBeFalsy()
      expect(state.reportFailed).toBeFalsy()
    })

    it('REPORT_FORM_CLOSED resets state', () => {
      state.isReportSent = true
      state.reportFailed = true
      state.isReportFormVisible = true
      mutations[REPORT_FORM_CLOSED](state)

      expect(state.isReportFormVisible).toBeFalsy()
      expect(state.isReportSent).toBeFalsy()
      expect(state.reportFailed).toBeFalsy()
    })
  })

  describe('actions', () => {
    let actions = null
    let reportServiceMock = null
    let commit = null

    beforeEach(() => {
      reportServiceMock = { sendReport: jest.fn(() => Promise.resolve({})) }
      commit = jest.fn()

      actions = store.actions(reportServiceMock)
    })

    it('SEND_CONTENT_REPORT on success', (done) => {
      const params = { foo: 'bar' }
      const action = actions[SEND_CONTENT_REPORT]
      action({ commit }, params).then(() => {
        expect(reportServiceMock.sendReport).toBeCalledWith(params)
        expect(commit).toBeCalledWith(REPORT_SENT)
        done()
      })
    })

    it('SEND_CONTENT_REPORT on failure', (done) => {
      reportServiceMock = { sendReport: jest.fn(() => Promise.reject({})) }
      actions = store.actions(reportServiceMock)

      const params = { foo: 'bar' }
      const action = actions[SEND_CONTENT_REPORT]
      action({ commit }, params).then(() => {
        expect(reportServiceMock.sendReport).toBeCalledWith(params)
        expect(commit).toBeCalledWith(REPORT_ERROR)
        done()
      })
    })
  })
})
