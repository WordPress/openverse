<template>
  <section>
    <VGridSkeleton
      v-if="results.length === 0 && !fetchState.isFinished"
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
    <VAudioList
      :collection-label="collectionLabel"
      :is-related="isRelated"
      :results="results"
    />
    <footer v-if="!isRelated">
      <VLoadMore />
    </footer>
  </section>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import type { FetchState } from "~/types/fetch-state"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"

import VAudioList from "~/components/VSearchResultsGrid/VAudioList.vue"
import VLoadMore from "~/components/VLoadMore.vue"
import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"
import VSnackbar from "~/components/VSnackbar.vue"

import type { NuxtError } from "@nuxt/types"

/**
 * This component shows a loading skeleton if the results are not yet loaded,
 * and then shows the list of audio, with the Load more button if needed.
 */
export default defineComponent({
  name: "VAudioCollection",
  components: {
    VSnackbar,
    VAudioList,
    VGridSkeleton,
    VLoadMore,
  },
  props: {
    results: {
      type: Array as PropType<AudioDetail[]>,
      default: () => [],
    },
    /**
     * If used for Related audio, do not show the Load more button.
     */
    isRelated: {
      type: Boolean,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState<NuxtError> | FetchState>,
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
