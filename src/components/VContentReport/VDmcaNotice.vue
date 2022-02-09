<template>
  <i18n
    class="dmca-notice"
    path="media-details.content-report.form.dmca.note"
    tag="p"
  >
    <template #form>
      <a
        :aria-label="$t('media-details.content-report.form.dmca.form')"
        :href="DMCA_FORM_URL"
        class="text-pink hover:underline"
        target="_blank"
        rel="noopener"
        >{{ $t('media-details.content-report.form.dmca.form') }}</a
      >
    </template>
    <template #source>
      <a
        :href="foreignLandingUrl"
        class="text-pink hover:underline"
        target="_blank"
        rel="noopener noreferrer"
        >{{ provider }}</a
      >
    </template>
  </i18n>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import { DMCA_FORM_URL } from '~/constants/content-report'

export default defineComponent({
  name: 'VDmcaNotice',
  props: {
    /**
     * the foreign landing URL for the media item
     */
    foreignLandingUrl: {
      type: String,
      required: true,
    },
    /**
     * the name of the provider of the media item
     */
    provider: {
      type: String,
      required: true,
    },
  },
  setup() {
    return {
      DMCA_FORM_URL,
    }
  },
})
</script>
