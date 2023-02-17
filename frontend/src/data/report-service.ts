import type { MediaType } from "~/constants/media"
import type { ReportReason } from "~/constants/content-report"
import { createApiService, getResourceSlug } from "~/data/api-service"

interface ReportParams {
  mediaType: MediaType
  identifier: string
  reason: ReportReason
  description?: string
}

const apiService = createApiService()
const ReportService = {
  sendReport(params: ReportParams) {
    const mediaType = params.mediaType
    return apiService.post(
      `/${getResourceSlug(mediaType)}${params.identifier}/report`,
      params
    )
  },
}

export default ReportService
