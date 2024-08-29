<script setup lang="ts">
import { useAnalytics } from "~/composables/use-analytics"

import { useSearchStore } from "~/stores/search"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"

/**
 * This link takes the user from a single result back to the list of all
 * results. It only appears if the user navigated from the search results.
 */
const props = defineProps<{
  /**
   * The unique ID of the media
   */
  id: string
  href: string
}>()

const { sendCustomEvent } = useAnalytics()
const searchStore = useSearchStore()

const handleClick = () => {
  sendCustomEvent("BACK_TO_SEARCH", {
    id: props.id,
    searchType: searchStore.searchType,
  })
}
</script>

<template>
  <!-- @todo: Separate the absolute container from the link itself. -->
  <VButton
    as="VLink"
    :href="href"
    has-icon-start
    variant="transparent-gray"
    size="small"
    class="label-bold inline-flex"
    @mousedown="handleClick"
  >
    <VIcon name="chevron-back" :rtl-flip="true" />
    {{ $t("singleResult.back") }}
  </VButton>
</template>
