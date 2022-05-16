<template>
  <div>
    <h5
      id="copy-license-title"
      class="mb-4 text-base md:text-2xl font-semibold"
    >
      {{ $t('media-details.reuse.copy-license.title') }}
    </h5>

    <VTabs label="#copy-license-title">
      <template #tabs>
        <VTab v-for="tab in tabs" :id="tab" :key="tab">
          {{ $t(`media-details.reuse.copy-license.${tab}`) }}
        </VTab>
      </template>
      <VLicenseTabPanel :tab="tabs[0]">
        <!-- Disable reason: We control the attribution HTML generation so this is safe and will not lead to XSS attacks -->
        <!-- eslint-disable vue/no-v-html -->
        <div v-html="getAttributionMarkup({ includeIcons: false })" />
        <!-- eslint-enable vue/no-v-html -->
      </VLicenseTabPanel>
      <VLicenseTabPanel :tab="tabs[1]">
        <p id="attribution-html" class="font-mono break-all" dir="ltr">
          {{ getAttributionMarkup() }}
        </p>
      </VLicenseTabPanel>
      <VLicenseTabPanel :tab="tabs[2]">
        {{ getAttributionMarkup({ isPlaintext: true }) }}
      </VLicenseTabPanel>
    </VTabs>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from '@nuxtjs/composition-api'

import { AttributionOptions, getAttribution } from '~/utils/attribution-html'

import type { Media } from '~/models/media'

import { useI18n } from '~/composables/use-i18n'

import VTabs from '~/components/VTabs/VTabs.vue'
import VTab from '~/components/VTabs/VTab.vue'
import VLicenseTabPanel from '~/components/VMediaInfo/VLicenseTabPanel.vue'

const tabs = ['rich', 'html', 'plain']

export default defineComponent({
  name: 'VCopyLicense',
  components: { VTabs, VTab, VLicenseTabPanel },
  props: {
    media: {
      type: Object as PropType<Media>,
      required: true,
    },
  },
  setup(props) {
    const i18n = useI18n()
    const getAttributionMarkup = (options?: AttributionOptions) =>
      getAttribution(props.media, i18n, options)
    return {
      tabs,

      getAttributionMarkup,
    }
  },
})
</script>
