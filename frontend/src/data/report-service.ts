import { MediaType } from "~/constants/media"
import type { ReportReason } from "~/constants/content-report"
import {
  type ApiService,
  createApiService,
  getResourceSlug,
} from "~/data/api-service"

interface ReportParams {
  mediaType: MediaType
  identifier: string
  reason: ReportReason
  description?: string
}
class ReportService {
  private readonly apiService: ApiService
  constructor(apiService: ApiService) {
    this.apiService = apiService
  }
  sendReport(params: ReportParams) {
    const mediaType = params.mediaType
    return this.apiService.post(
      `/${getResourceSlug(mediaType)}${params.identifier}/report`,
      params
    )
  }
}

export const initReportService = (accessToken?: string) => {
  return new ReportService(createApiService({ accessToken }))
}
