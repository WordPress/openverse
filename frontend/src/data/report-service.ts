import type { MediaType } from "~/constants/media"
import { ReportReason, SENSITIVE } from "~/constants/content-report"
import { createApiService, getResourceSlug } from "~/data/api-service"

interface ReportParams {
  mediaType: MediaType
  identifier: string
  reason: ReportReason
  description?: string
}

interface LegacyAPIParams extends Omit<ReportParams, "reason"> {
  reason: Exclude<ReportReason, "sensitive"> | "mature"
}

/**
 * Map report parameters to the legacy parameters temporarily expected
 * by the Openverse API.
 *
 * Specifically, the Openverse API expects a "mature" reason instead
 * of a "sensitive" reason, so this function maps `reason` from `sensitive`
 * to `mature`. Once the Openverse API handles `sensitive` reason, this
 * function can be removed.
 *
 * The API work chain starts with this issue:
 * https://github.com/WordPress/openverse/issues/2626
 * @param params Content report modal parameters
 * @returns Parameters mapped to match Openverse API expectations
 */
const mapToLegacy = (params: ReportParams): LegacyAPIParams => ({
  ...params,
  reason: params.reason === SENSITIVE ? "mature" : params.reason,
})

const apiService = createApiService()
const ReportService = {
  sendReport(params: ReportParams) {
    const mediaType = params.mediaType
    return apiService.post(
      `/${getResourceSlug(mediaType)}${params.identifier}/report`,
      mapToLegacy(params)
    )
  },
}

export default ReportService
