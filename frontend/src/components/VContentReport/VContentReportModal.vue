<script setup lang="ts">
import { ref } from "vue"

import { WIP } from "~/constants/content-report"
import { useContentReport } from "~/composables/use-content-report"
import type { AudioDetail, ImageDetail } from "~/types/media"

import VContentReportButton from "~/components/VContentReport/VContentReportButton.vue"
import VContentReportForm from "~/components/VContentReport/VContentReportForm.vue"
import VModal from "~/components/VModal/VModal.vue"

defineProps<{
  /**
   * The media item to report. This can either be an audio track or an image.
   */
  media: AudioDetail | ImageDetail
}>()

const modalRef = ref<InstanceType<typeof VModal> | null>(null)
const contentReportFormRef = ref<InstanceType<
  typeof VContentReportForm
> | null>(null)

const { status, updateStatus, title } = useContentReport()

const resetForm = () => {
  contentReportFormRef.value?.resetForm()
  updateStatus(WIP)
}

const close = () => {
  resetForm()
  modalRef.value?.close()
}
</script>

<template>
  <VModal
    ref="modalRef"
    :label="$t('mediaDetails.contentReport.long')"
    :hide-on-click-outside="true"
    variant="centered"
    @close="resetForm"
  >
    <template #trigger="{ a11yProps }">
      <VContentReportButton v-bind="a11yProps" />
    </template>
    <template #title>
      <h2 class="heading-6" tabindex="-1">{{ title }}</h2>
    </template>
    <template #default>
      <VContentReportForm
        ref="contentReportFormRef"
        class="p-7 pt-0 sm:p-9"
        :media="media"
        :status="status"
        :allow-cancel="true"
        @update-status="updateStatus"
        @close="close"
      >
      </VContentReportForm>
    </template>
  </VModal>
</template>
