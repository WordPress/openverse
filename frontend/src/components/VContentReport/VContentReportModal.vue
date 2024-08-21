<script setup lang="ts">
import { computed, ref } from "vue"

import type { AudioDetail, ImageDetail } from "~/types/media"

import VContentReportButton from "~/components/VContentReport/VContentReportButton.vue"
import VContentReportForm from "~/components/VContentReport/VContentReportForm.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"
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

const close = () => {
  contentReportFormRef.value?.resetForm()
  modalRef.value?.close()
}

const dialogRef = ref<HTMLElement | undefined>(undefined)
const initialFocusElement = computed(
  () => dialogRef.value?.querySelector("h2") ?? undefined
)
</script>

<template>
  <VModal
    ref="modalRef"
    :initial-focus-element="initialFocusElement"
    :label="$t('mediaDetails.contentReport.long')"
    variant="centered"
  >
    <template #trigger="{ a11yProps }">
      <VContentReportButton v-bind="a11yProps" />
    </template>
    <template #default>
      <div ref="dialogRef" class="pe-1 ps-3">
        <VContentReportForm
          ref="contentReportFormRef"
          class="-mt-6 p-6"
          :close-fn="close"
          :media="media"
          :provider-name="media.providerName"
        >
          <template #close-button>
            <VIconButton
              :label="$t('modal.close')"
              :icon-props="{ name: 'close' }"
              variant="transparent-gray"
              size="small"
              @click="close"
            />
          </template>
        </VContentReportForm>
      </div>
    </template>
  </VModal>
</template>
