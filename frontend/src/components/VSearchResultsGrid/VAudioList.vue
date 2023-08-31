<template>
  <!-- Negative margin compensates for the `p-4` padding in row layout. -->
  <ol
    :aria-label="collectionLabel"
    class="-mx-2 flex flex-col md:-mx-4"
    :class="isRelated ? 'gap-4' : 'gap-2 md:gap-1'"
  >
    <VAudioResult
      v-for="audio in results"
      :key="audio.id"
      :search-term="searchTerm"
      :audio="audio"
      layout="row"
      :size="audioTrackSize"
      :is-related="isRelated"
    />
  </ol>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import VAudioResult from "~/components/VSearchResultsGrid/VAudioResult.vue"

/**
 * The list of audio for the search results and the related audio.
 */
export default defineComponent({
  name: "VAudioList",
  components: { VAudioResult },
  props: {
    results: {
      type: Array as PropType<AudioDetail[]>,
      default: () => [],
    },
    isRelated: {
      type: Boolean,
      required: true,
    },
    /**
     * The label used for the list of audio for accessibility.
     */
    collectionLabel: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const uiStore = useUiStore()

    const audioTrackSize = computed(() => {
      if (props.isRelated) {
        return uiStore.isBreakpoint("md") ? "m" : "s"
      } else {
        return !uiStore.isDesktopLayout
          ? "s"
          : uiStore.isFilterVisible
          ? "l"
          : "m"
      }
    })

    const searchStore = useSearchStore()
    const searchTerm = computed(() => searchStore.searchTerm)

    return {
      audioTrackSize,
      searchTerm,
    }
  },
})
</script>
