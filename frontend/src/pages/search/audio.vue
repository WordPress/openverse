<template>
  <!-- Negative margin compensates for the `p-4` padding in row layout. -->
  <section class="-mx-2 md:-mx-4">
    <VSnackbar size="large" :is-visible="snackbar.isVisible.value">
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
    <VGridSkeleton
      v-if="results.length === 0 && !fetchState.isFinished"
      is-for-tab="audio"
    />
    <ol :aria-label="$t('browsePage.aria.results', { query: searchTerm })">
      <li v-for="audio in results" :key="audio.id">
        <VAudioTrack
          class="mb-2 md:mb-1"
          :audio="audio"
          :size="audioTrackSize"
          layout="row"
          :search-term="searchTerm"
          @interacted="handleInteraction"
          @mousedown="snackbar.handleMouseDown"
          @focus="snackbar.show"
        />
      </li>
    </ol>
    <VLoadMore />
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, inject } from "vue"

import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import { useAnalytics } from "~/composables/use-analytics"
import { useAudioSnackbar } from "~/composables/use-audio-snackbar"

import { IsSidebarVisibleKey } from "~/types/provides"
import type { AudioInteractionData } from "~/types/analytics"

import VSnackbar from "~/components/VSnackbar.vue"
import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"
import VLoadMore from "~/components/VLoadMore.vue"
import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"

import { propTypes } from "./search-page.types"

export default defineComponent({
  name: "AudioSearch",
  components: {
    VSnackbar,
    VAudioTrack,
    VGridSkeleton,
    VLoadMore,
  },
  props: propTypes,
  setup(props) {
    const searchStore = useSearchStore()

    const uiStore = useUiStore()

    const { sendCustomEvent } = useAnalytics()

    const searchTerm = computed(() => searchStore.searchTerm)
    const results = computed(() => props.resultItems.audio)

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
    const filterVisibleRef = inject(IsSidebarVisibleKey)

    const audioTrackSize = computed(() =>
      !isDesktopLayout.value ? "s" : filterVisibleRef.value ? "l" : "m"
    )

    const snackbar = useAudioSnackbar()

    const handleInteraction = (data: AudioInteractionData) => {
      snackbar.hide()
      sendCustomEvent("AUDIO_INTERACTION", {
        ...data,
        component: "AudioSearch",
      })
    }

    return {
      searchTerm,
      results,
      audioTrackSize,

      handleInteraction,
      snackbar,
    }
  },
})
</script>
