<template>
  <section>
    <VGridSkeleton
      v-if="results && results.length === 0 && !fetchState.isFinished"
      is-for-tab="audio"
    />
    <VSnackbar size="large" :is-visible="isSnackbarVisible">
      <i18n path="audioResults.snackbar.text" tag="p">
        <template
          v-for="keyboardKey in ['spacebar', 'left', 'right']"
          #[keyboardKey]
        >
          <kbd :key="keyboardKey" class="font-sans">{{
            $t(`audioResults.snackbar.${keyboardKey}`)
          }}</kbd>
        </template>
      </i18n>
    </VSnackbar>
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
        :audio="audio"
        layout="row"
        :size="audioTrackSize"
        :kind="kind"
      />
    </ol>
    <footer v-if="kind !== 'related'" class="mt-4">
      <VLoadMoreOld />
    </footer>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import type { FetchState } from "~/types/fetch-state"
import type { ResultKind } from "~/types/result"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"

import { useSearchStore } from "~/stores/search"

import { useUiStore } from "~/stores/ui"

import VLoadMoreOld from "~/components/VLoadMoreOld.vue"
import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"
import VSnackbar from "~/components/VSnackbar.vue"
import VAudioResult from "~/components/VSearchResultsGrid/VAudioResult.vue"

/**
 * This component shows a loading skeleton if the results are not yet loaded,
 * and then shows the list of audio, with the Load more button if needed.
 */
export default defineComponent({
  name: "VAudioList",
  components: {
    VAudioResult,
    VSnackbar,
    VGridSkeleton,
    VLoadMoreOld,
  },
  props: {
    results: {
      type: Array as PropType<AudioDetail[]>,
      default: () => [],
    },
    /**
     * If used for Related audio, do not show the Load more button.
     */
    kind: {
      type: String as PropType<ResultKind>,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState>,
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
    const { isVisible: isSnackbarVisible } = useAudioSnackbar()

    const uiStore = useUiStore()

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

    const searchStore = useSearchStore()
    const searchTerm = computed(() => searchStore.searchTerm)

    return {
      audioTrackSize,
      searchTerm,
      isSnackbarVisible,
    }
  },
})
</script>
