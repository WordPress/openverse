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
      @copied="handleCopy"
    />
  </VTabPanel>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { MediaType } from "~/constants/media"

import { useAnalytics } from "~/composables/use-analytics"

import VCopyButton from "~/components/VCopyButton.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"

export default defineComponent({
  name: "VLicenseTabPanel",
  components: {
    VCopyButton,
    VTabPanel,
  },
  props: {
    /**
     * The kind of attribution shown in the tab.
     */
    tab: {
      type: String as PropType<"rich" | "html" | "plain">,
      required: true,
    },
    /**
     * The ID of the media for which the attribution is generated.
     * Used for analytics.
     */
    mediaId: {
      type: String,
      required: true,
    },
    /**
     * The media type of the media for which the attribution is generated.
     * Used for analytics.
     */
    mediaType: {
      type: String as PropType<MediaType>,
      required: true,
    },
  },
  setup(props) {
    const { sendCustomEvent } = useAnalytics()
    const handleCopy = () => {
      sendCustomEvent("COPY_ATTRIBUTION", {
        id: props.mediaId,
        format: props.tab,
        mediaType: props.mediaType,
      })
    }
    return {
      handleCopy,
    }
  },
})
</script>
