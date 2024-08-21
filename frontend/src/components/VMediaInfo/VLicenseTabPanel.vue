<script setup lang="ts">
import { useNuxtApp } from "#imports"

import type { MediaType } from "~/constants/media"

import VCopyButton from "~/components/VCopyButton.vue"
import VTabPanel from "~/components/VTabs/VTabPanel.vue"

const props = defineProps<{
  /**
   * The kind of attribution shown in the tab.
   */
  tab: "rich" | "html" | "plain" | "xml"
  /**
   * The ID of the media for which the attribution is generated.
   * Used for analytics.
   */
  mediaId: string
  /**
   * The media type of the media for which the attribution is generated.
   * Used for analytics.
   */
  mediaType: MediaType
}>()

const { $sendCustomEvent } = useNuxtApp()
const handleCopy = () => {
  $sendCustomEvent("COPY_ATTRIBUTION", {
    id: props.mediaId,
    format: props.tab,
    mediaType: props.mediaType,
  })
}
</script>

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
