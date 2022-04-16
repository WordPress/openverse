import type { MediaType } from '~/constants/media'
import type { ReportReason } from '~/constants/content-report'
import { getResourceSlug, VersionedApiService } from '~/data/api-service'

interface ReportParams {
  mediaType: MediaType
  identifier: string
  reason: ReportReason
  description?: string
}
const ReportService = {
  sendReport(params: ReportParams) {
    const mediaType = params.mediaType
    return VersionedApiService.post(
      `/${getResourceSlug(mediaType)}${params.identifier}/report`,
      params
    )
  },
}

export default ReportService
