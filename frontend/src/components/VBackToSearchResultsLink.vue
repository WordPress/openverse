<template>
  <!-- @todo: Separate the absolute container from the link itself. -->
  <VLink
    class="time inline-flex flex-row items-center gap-2 rounded-sm p-2 pe-3 text-xs font-semibold text-dark-charcoal-70 hover:text-dark-charcoal"
    v-bind="$attrs"
    @mousedown="handleClick"
  >
    <VIcon name="chevron-left" :rtl-flip="true" />
    {{ $t("single-result.back") }}
  </VLink>
</template>

<script lang="ts">
import { defineComponent } from "vue"

import { useAnalytics } from "~/composables/use-analytics"
import { useSearchStore } from "~/stores/search"

import VIcon from "~/components/VIcon/VIcon.vue"
import VLink from "~/components/VLink.vue"

/**
 * This link takes the user from a single result back to the list of all
 * results. It only appears if the user navigated from the search results.
 */
export default defineComponent({
  components: {
    VIcon,
    VLink,
  },
  inheritAttrs: false,
  props: {
    /**
     * The unique ID of the media
     */
    id: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const { sendCustomEvent } = useAnalytics()
    const searchStore = useSearchStore()

    const handleClick = () => {
      sendCustomEvent("BACK_TO_SEARCH", {
        id: props.id,
        searchType: searchStore.searchType,
      })
    }

    return {
      handleClick,
    }
  },
})
</script>
