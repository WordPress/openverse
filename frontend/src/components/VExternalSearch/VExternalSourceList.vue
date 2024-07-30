<template>
  <div
    class="p-4 pt-0 sm:max-w-[25rem] sm:p-6 sm:pt-0"
    data-testid="source-list-popover"
  >
    <p class="label-regular px-3 py-4 text-start !leading-normal">
      {{ $t("externalSources.caption", { openverse: "Openverse" }) }}
    </p>
    <VButton
      v-for="source in externalSources"
      :key="source.name"
      as="VLink"
      variant="transparent-gray"
      size="medium"
      class="label-regular !w-full justify-between"
      show-external-icon
      has-icon-end
      :external-icon-size="6"
      :href="source.url"
      :send-external-link-click-event="false"
      @mousedown="handleClick(source.name)"
    >
      {{ source.name }}
    </VButton>
  </div>
</template>

<script setup lang="ts">
import { useAnalytics } from "~/composables/use-analytics"

import { useExternalSources } from "~/composables/use-external-sources"

import VButton from "~/components/VButton.vue"

/**
 * This component renders a list of pre-populated links to additional sources
 * when there are insufficient or zero search results.
 */
const props = defineProps<{
  /**
   * The search term for which the external sources links are generated.
   */
  searchTerm: string
}>()

const { externalSources, externalSourcesType } = useExternalSources()

const { sendCustomEvent } = useAnalytics()
const handleClick = (sourceName: string) => {
  sendCustomEvent("SELECT_EXTERNAL_SOURCE", {
    name: sourceName,
    mediaType: externalSourcesType.value,
    query: props.searchTerm,
    component: "VExternalSourceList",
  })
}
</script>
