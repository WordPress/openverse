import ApiService from './ApiService'

const BugReportService = {
  reportBug(bugReport) {
    return ApiService.post('/report-bug', bugReport)
  },
}

export default BugReportService
