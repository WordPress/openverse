import { getResourceSlug, VersionedApiService } from '~/data/api-service'

import { IMAGE } from '~/constants/media'

const ReportService = {
  sendReport(params) {
    const mediaType = params.mediaType ?? IMAGE
    return VersionedApiService.post(
      `/${getResourceSlug(mediaType)}${params.identifier}/report`,
      params
    )
  },
}

export default ReportService
