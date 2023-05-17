<template>
  <VPopover
    ref="popoverEl"
    :hide-on-click-outside="false"
    :label="$t('media-details.content-report.long').toString()"
    placement="bottom-end"
    width="w-80"
  >
    <template #trigger="{ a11yProps }">
      <VContentReportButton v-bind="a11yProps" />
    </template>
    <template #default="{ close }">
      <div class="grid w-80 items-stretch justify-stretch">
        <VCloseButton
          :label="$t('modal.close')"
          class="z-10 col-start-1 row-start-1 self-start justify-self-end"
          @close="close"
        />
        <VContentReportForm
          class="col-start-1 row-start-1 p-6"
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
