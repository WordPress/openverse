<template>
  <section>
    <VSnackbar size="large" :is-visible="isSnackbarVisible">
      <i18n-t scope="global" keypath="audioResults.snackbar.text" tag="p">
        <template
          v-for="keyboardKey in ['spacebar', 'left', 'right']"
          :key="keyboardKey"
          #[keyboardKey]
        >
          <kbd class="font-sans">{{
            $t(`audioResults.snackbar.${keyboardKey}`)
          }}</kbd>
        </template>
      </i18n-t>
    </VSnackbar>
    <VAudioList
      :collection-label="collectionLabel"
      :kind="kind"
      :results="results"
    />
  </section>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import type { FetchState } from "~/types/fetch-state"
import type { ResultKind } from "~/types/result"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"

import VAudioList from "~/components/VSearchResultsGrid/VAudioList.vue"
import VSnackbar from "~/components/VSnackbar.vue"

/**
 * This component shows a loading skeleton if the results are not yet loaded,
 * and then shows the list of audio, with the Load more button if needed.
 */
export default defineComponent({
  name: "VAudioCollection",
  components: {
    VSnackbar,
    VAudioList,
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
  setup() {
    const { isVisible: isSnackbarVisible } = useAudioSnackbar()

    return {
      isSnackbarVisible,
    }
  },
})
</script>
