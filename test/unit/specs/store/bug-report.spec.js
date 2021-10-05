import {
  state,
  mutations as BugReportMutations,
  createActions,
} from '~/store/bug-report'
import {
  REPORT_BUG_START,
  REPORT_BUG_END,
  REPORT_BUG_FAILED,
} from '~/constants/mutation-types'
import { REPORT_BUG } from '~/constants/action-types'

describe('Attribution Store', () => {
  describe('actions', () => {
    let serviceMock = null
    let commitMock = null
    let store = {}

    const data = {
      name: 'Foo',
      email: 'foo@bar.com',
      bug_description: 'FooBar',
      browser_info: 'Foo browser',
    }

    beforeEach(() => {
      serviceMock = {
        reportBug: jest.fn(),
      }
      commitMock = {
        commit: jest.fn(),
      }
      serviceMock.reportBug.mockResolvedValue(1)
      store = {
        state: state(),
        mutations: BugReportMutations,
        actions: createActions(serviceMock),
      }
    })

    it('calls reportBug service', () => {
      store.actions[REPORT_BUG](commitMock, data)

      expect(serviceMock.reportBug).toHaveBeenCalledWith(data)
    })

    it('commits REPORT_BUG_START', () => {
      store.actions.REPORT_BUG(commitMock, data)

      expect(commitMock.commit).toHaveBeenCalledWith(REPORT_BUG_START)
    })

    it('commits REPORT_BUG_END', (done) => {
      store.actions.REPORT_BUG(commitMock, data)

      setTimeout(() => {
        expect(commitMock.commit).toHaveBeenCalledWith(REPORT_BUG_END)
        done()
      }, 10)
    })

    it('commits REPORT_BUG_FAILED', (done) => {
      const failedServiceMock = {
        reportBug: jest.fn(),
      }
      store.actions = createActions(failedServiceMock)
      failedServiceMock.reportBug.mockRejectedValue(1)
      store.actions.REPORT_BUG(commitMock, data)

      setTimeout(() => {
        expect(commitMock.commit).toHaveBeenCalledWith(REPORT_BUG_FAILED)
        done()
      }, 10)
    })
  })

  describe('mutations', () => {
    let state = null
    let mutations = null

    beforeEach(() => {
      state = {}
      mutations = BugReportMutations
    })

    it('REPORT_BUG_START sets isReportingBug to true', () => {
      mutations.REPORT_BUG_START(state)

      expect(state.isReportingBug).toBeTruthy()
    })

    it('REPORT_BUG_END sets bugReported to true and isReportingBug to false', () => {
      mutations.REPORT_BUG_END(state)

      expect(state.bugReported).toBeTruthy()
      expect(state.isReportingBug).toBeFalsy()
    })

    it('REPORT_BUG_FAILED sets bugReportFailed to true and isReportingBug to false', () => {
      mutations.REPORT_BUG_FAILED(state)

      expect(state.bugReportFailed).toBeTruthy()
      expect(state.isReportingBug).toBeFalsy()
    })
  })
})
