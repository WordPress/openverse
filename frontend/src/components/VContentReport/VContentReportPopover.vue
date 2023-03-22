<template>
  <VPopover
    ref="popoverEl"
    :hide-on-click-outside="false"
    :label="$t('media-details.content-report.long').toString()"
    placement="bottom-end"
  >
    <template #trigger="{ a11yProps }">
      <VContentReportButton v-bind="a11yProps" />
    </template>
    <template #default="{ close }">
      <div class="relative" data-testid="content-report-popover">
        <VCloseButton
          :label="$t('modal.close')"
          class="!absolute top-0 end-0"
          @close="close"
        />
        <VContentReportForm
          class="w-80 p-6"
          :close-fn="close"
          :media="media"
          :provider-name="media.providerName || media.provider"
        />
      </div>
    </template>
  </VPopover>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioDetail, ImageDetail } from "~/types/media"

import VCloseButton from "~/components/VCloseButton.vue"
import VContentReportButton from "~/components/VContentReport/VContentReportButton.vue"
import VContentReportForm from "~/components/VContentReport/VContentReportForm.vue"
import VPopover from "~/components/VPopover/VPopover.vue"

export default defineComponent({
  name: "VContentReportPopover",
  components: {
    VCloseButton,
    VContentReportButton,
    VContentReportForm,
    VPopover,
  },
  props: {
    /**
     * the media item to report; This can either be an audio track or an image.
     */
    media: {
      type: Object as PropType<AudioDetail | ImageDetail>,
      required: true,
    },
  },
})
</script>
