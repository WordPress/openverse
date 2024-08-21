import { useI18n } from "#imports"

import { computed, ref } from "vue"

import { type ReportStatus, SENT, WIP } from "~/constants/content-report"

export const useContentReport = () => {
  const status = ref<ReportStatus>(WIP)

  const updateStatus = (newStatus: ReportStatus) => {
    status.value = newStatus
  }

  const { t } = useI18n({ useScope: "global" })

  const title = computed(() => {
    return status.value === WIP
      ? t("mediaDetails.contentReport.long")
      : status.value === SENT
        ? t("mediaDetails.contentReport.success.title")
        : t("mediaDetails.contentReport.failure.title")
  })

  return {
    status,
    updateStatus,
    title,
  }
}
