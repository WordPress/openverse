<template>
  <VTabPanel
    :id="tab"
    class="flex h-[190px] flex-col items-start justify-between text-sm md:text-base"
  >
    <div :id="`panel-slot-${tab}`" class="overflow-y-auto">
      <slot />
    </div>
    <VCopyButton
      :id="`copyattr-${tab}`"
      :el="`#panel-slot-${tab}`"
      class="mt-6"
    />
  </VTabPanel>
</template>

<script lang="ts">
import { defineComponent } from "vue"

import VCopyButton from "~/components/VCopyButton.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"

export default defineComponent({
  name: "VLicenseTabPanel",
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
