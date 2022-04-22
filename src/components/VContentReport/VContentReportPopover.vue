<template>
  <VPopover
    ref="popoverEl"
    :hide-on-click-outside="false"
    :label="$t('media-details.content-report.long')"
    placement="bottom-end"
  >
    <template #trigger="{ a11yProps }">
      <VContentReportButton v-bind="a11yProps" />
    </template>
    <template #default="{ close }">
      <div class="relative" data-testid="content-report-popover">
        <VIconButton
          class="absolute top-0 end-0 border-none text-dark-charcoal-70"
          size="search-medium"
          :icon-props="{ iconPath: icons.closeSmall }"
          :button-props="{
            'aria-label': $t('modal.close').toString(),
            variant: 'plain',
          }"
          @click="close"
        />
        <VContentReportForm
          :close-fn="close"
          :media="media"
          :provider-name="media.providerName"
        />
      </div>
    </template>
  </VPopover>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import VIconButton from '~/components/VIconButton/VIconButton.vue'
import VPopover from '~/components/VPopover/VPopover.vue'
import VContentReportButton from '~/components/VContentReport/VContentReportButton.vue'
import VContentReportForm from '~/components/VContentReport/VContentReportForm.vue'

import flagIcon from '~/assets/icons/flag.svg'
import closeSmallIcon from '~/assets/icons/close-small.svg'

export default defineComponent({
  name: 'VContentReportPopover',
  components: {
    VIconButton,
    VPopover,
    VContentReportButton,
    VContentReportForm,
  },
  props: {
    /**
     * the media item to report; This can either be an audio track or an image.
     */
    media: {
      type: Object,
      required: true,
    },
  },
  setup() {
    return {
      icons: { flag: flagIcon, closeSmall: closeSmallIcon },
    }
  },
})
</script>
