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
            t(`audioResults.snackbar.${keyboardKey}`)
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

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import type { AudioDetail } from "~/types/media"
import type { ResultKind } from "~/types/result"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"

import VAudioList from "~/components/VSearchResultsGrid/VAudioList.vue"
import VSnackbar from "~/components/VSnackbar.vue"

/**
 * This component shows a loading skeleton if the results are not yet loaded,
 * and then shows the list of audio, with the Load more button if needed.
 */
defineProps<{
  results: AudioDetail[]
  kind: ResultKind
  collectionLabel: string
}>()

const {
  $i18n: { t },
} = useNuxtApp()

const { isVisible: isSnackbarVisible } = useAudioSnackbar()
</script>
