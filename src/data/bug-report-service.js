import ApiService from './api-service'

const BugReportService = {
  reportBug(bugReport) {
    return ApiService.post('/report-bug', bugReport)
  },
}

export default BugReportService
