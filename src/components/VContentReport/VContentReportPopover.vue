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
      <div class="relative">
        <VIconButton
          class="absolute top-0 end-0 border-none"
          size="search-medium"
          :icon-props="{ iconPath: icons.closeSmall }"
          @click="close"
        />
        <VContentReportForm
          :close-fn="close"
          :media="media"
          :provider-name="providerName"
        />
      </div>
    </template>
  </VPopover>
</template>

<script>
import { computed, useStore, defineComponent } from '@nuxtjs/composition-api'

import VPopover from '~/components/VPopover/VPopover.vue'

import VContentReportButton from '~/components/VContentReport/VContentReportButton.vue'

import flagIcon from '~/assets/icons/flag.svg'

import closeSmallIcon from '~/assets/icons/close-small.svg'

export default defineComponent({
  name: 'VContentReportPopover',
  components: { VPopover, VContentReportButton },
  props: {
    /**
     * the media item to report; This can either be an audio track or an image.
     */
    media: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    const store = useStore()

    const getProviderName = (nameCode) =>
      store.getters['provider/getProviderName'](nameCode)
    const providerName = computed(() => getProviderName(props.media.provider))

    return {
      icons: { flag: flagIcon, closeSmall: closeSmallIcon },

      providerName,
    }
  },
})
</script>
