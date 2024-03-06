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

<script lang="ts">
import { computed, defineComponent, type PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import type { ResultKind } from "~/types/result"

import { useUiStore } from "~/stores/ui"

import VAudioResult from "~/components/VSearchResultsGrid/VAudioResult.vue"
import VAudioInstructions from "~/components/VSearchResultsGrid/VAudioInstructions.vue"

/**
 * This component shows a loading skeleton if the results are not yet loaded,
 * and then shows the list of audio, with the Load more button if needed.
 */
export default defineComponent({
  name: "VAudioCollection",
  components: {
    VAudioInstructions,
    VAudioResult,
  },
  props: {
    results: {
      type: Array as PropType<AudioDetail[]>,
      required: true,
    },
    /**
     * If used for Related audio, do not show the Load more button.
     */
    kind: {
      type: String as PropType<ResultKind>,
      required: true,
    },
    /**
     * The label used for the list of audio for accessibility.
     */
    collectionLabel: {
      type: String,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
    relatedTo: {
      type: String as PropType<string | null>,
      default: null,
    },
  },
  setup(props) {
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

    return {
      audioTrackSize,
    }
  },
})
</script>
