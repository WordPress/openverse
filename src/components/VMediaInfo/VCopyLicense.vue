<template>
  <div>
    <h5 class="mb-4 text-base md:text-2xl font-semibold">
      {{ $t('media-details.reuse.copy-license.title') }}
    </h5>

    <nav class="flex border-b-none" role="tablist">
      <button
        v-for="(tab, idx) in tabs"
        :key="idx"
        role="tab"
        :aria-controls="`tab-${tab}`"
        :aria-selected="activeTab === tab"
        class="py-3 md:py-4 px-4 md:px-6 border-t border-x rounded-t-sm bg-white text-sm md:text-base font-semibold relative focus:border-tx focus:outline-none focus:shadow-[0_0_0_1.5px_#c52b9b_inset]"
        :class="[
          activeTab === tab
            ? 'border-t-dark-charcoal-20 border-x-dark-charcoal-20 -mb-[1px]'
            : 'border-tx',
        ]"
        @click.prevent="setActiveTab(tab)"
      >
        {{ $t(`media-details.reuse.copy-license.${tab}`) }}
      </button>
    </nav>

    <div
      v-for="(tab, idx) in tabs"
      :id="`tab-${tab}`"
      :key="idx"
      :aria-labelledby="tab"
      role="tabpanel"
      tabindex="0"
      class="border border-dark-charcoal-20 p-4 md:p-6 text-sm md:text-base focus:border-tx focus:outline-none focus:shadow-[0_0_0_1.5px_#c52b9b_inset] h-[190px] flex flex-col justify-between items-start"
      :class="{ hidden: activeTab !== tab }"
    >
      <div class="overflow-y-scroll">
        <!-- Disable reason: We control the attribution HTML generation so this is safe and will not lead to XSS attacks -->
        <!-- eslint-disable vue/no-v-html -->
        <div
          v-if="tab === 'rich'"
          id="attribution-rich"
          v-html="getAttributionMarkup({ includeIcons: false })"
        />
        <!-- eslint-enable vue/no-v-html -->

        <p
          v-if="tab === 'html'"
          id="attribution-html"
          class="font-mono break-all"
          dir="ltr"
        >
          {{ getAttributionMarkup() }}
        </p>

        <div v-if="tab === 'plain'" id="attribution-plain">
          {{ getAttributionMarkup({ isPlaintext: true }) }}
        </div>
      </div>

      <VCopyButton
        :id="`copyattr-${tab}`"
        :el="`#attribution-${tab}`"
        class="mt-6"
      />
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, useContext } from '@nuxtjs/composition-api'

import { getAttribution } from '~/utils/attribution-html'

import VCopyButton from '~/components/VCopyButton.vue'

const VCopyLicense = defineComponent({
  name: 'VCopyLicense',
  components: { VCopyButton },
  props: {
    media: {
      type: Object,
    },
  },
  setup(props) {
    const { i18n } = useContext()

    const activeTab = ref('rich')
    const tabs = ['rich', 'html', 'plain']

    const setActiveTab = (tabIdx) => (activeTab.value = tabIdx)

    const getAttributionMarkup = (options) =>
      getAttribution(props.media, i18n, options)

    return {
      activeTab,
      tabs,
      setActiveTab,

      getAttributionMarkup,
    }
  },
})
export default VCopyLicense
</script>
