<template>
  <VTabPanel
    :id="tab"
    class="h-[190px] flex flex-col justify-between items-start text-sm md:text-base"
  >
    <div class="overflow-y-auto">
      <slot />
    </div>
    <VCopyButton :id="`copyattr-${tab}`" :el="`#panel-${tab}`" class="mt-6" />
  </VTabPanel>
</template>

<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

import VCopyButton from '~/components/VCopyButton.vue'
import VTabPanel from '~/components/VTabs/VTabPanel.vue'

export default defineComponent({
  name: 'VLicenseTabPanel',
  components: {
    VCopyButton,
    VTabPanel,
  },
  props: {
    tab: {
      type: String,
      required: true,
    },
  },
})
</script>
