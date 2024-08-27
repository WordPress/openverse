<script setup lang="ts">
import { computed } from "vue"

import { useUiStore } from "~/stores/ui"

import type { CollectionComponentProps } from "~/types/collection-component-props"

import VAudioResult from "~/components/VSearchResultsGrid/VAudioResult.vue"
import VAudioInstructions from "~/components/VSearchResultsGrid/VAudioInstructions.vue"

/**
 * This component shows a loading skeleton if the results are not yet loaded,
 * and then shows the list of audio, with the Load more button if needed.
 */

const props = withDefaults(defineProps<CollectionComponentProps<"audio">>(), {
  kind: "search",
  relatedTo: "null",
})

const uiStore = useUiStore()

// Determine the size of the audio track based on the kind
// of collection and the current breakpoint.
const audioTrackSize = computed(() => {
  if (props.kind === "related") {
    return uiStore.isBreakpoint("sm") ? "m" : "s"
  } else {
    return !uiStore.isBreakpoint("sm")
      ? "s"
      : uiStore.isBreakpoint("xl")
        ? "l"
        : "m"
  }
})
</script>

<template>
  <div>
    <VAudioInstructions kind="audio" />
    <!-- Negative margin compensates for the `p-4` padding in row layout. -->
    <ol
      :aria-label="collectionLabel"
      class="-mx-2 flex flex-col md:-mx-4"
      :class="kind === 'related' ? 'gap-4' : 'gap-2 md:gap-1'"
    >
      <VAudioResult
        v-for="audio in results"
        :key="audio.id"
        :search-term="searchTerm"
        :related-to="relatedTo"
        :audio="audio"
        layout="row"
        :size="audioTrackSize"
        :kind="kind"
      />
    </ol>
  </div>
</template>
