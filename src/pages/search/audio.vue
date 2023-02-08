<template>
  <!-- Negative margin compensates for the `p-4` padding in row layout. -->
  <section class="-mx-2 md:-mx-4">
    <VSnackbar size="large" :is-visible="isSnackbarVisible">
      <i18n path="audio-results.snackbar.text" tag="p">
        <template
          v-for="keyboardKey in ['spacebar', 'left', 'right']"
          #[keyboardKey]
        >
          <kbd :key="keyboardKey" class="font-sans">{{
            $t(`audio-results.snackbar.${keyboardKey}`)
          }}</kbd>
        </template>
      </i18n>
    </VSnackbar>
    <VGridSkeleton
      v-if="results.length === 0 && !fetchState.isFinished"
      is-for-tab="audio"
    />
    <VAudioTrack
      v-for="(audio, i) in results"
      :key="audio.id"
      class="mb-2 md:mb-1"
      :audio="audio"
      :size="audioTrackSize"
      layout="row"
      :search-term="searchTerm"
      @shift-tab="handleShiftTab($event, i)"
      @interacted="hideSnackbar"
      @mousedown.native="handleMouseDown"
      @focus.native="showSnackbar"
    />
    <VLoadMore />
  </section>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  useMeta,
  ref,
  inject,
} from "@nuxtjs/composition-api"

import { useFocusFilters } from "~/composables/use-focus-filters"
import { useSearchStore } from "~/stores/search"

import { Focus } from "~/utils/focus-management"

import { useUiStore } from "~/stores/ui"

import { IsSidebarVisibleKey } from "~/types/provides"

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
    useMeta({
      title: `${props.searchTerm} | Openverse`,
    })
    const searchStore = useSearchStore()

    const uiStore = useUiStore()

    const searchTerm = computed(() => searchStore.searchTerm)
    const results = computed(() => props.resultItems.audio)

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)
    const filterVisibleRef = inject(IsSidebarVisibleKey)

    const audioTrackSize = computed(() =>
      !isDesktopLayout.value ? "s" : filterVisibleRef.value ? "l" : "m"
    )

    const focusFilters = useFocusFilters()
    const handleShiftTab = (event: KeyboardEvent, i: number) => {
      if (i === 0) {
        focusFilters.focusFilterSidebar(event, Focus.Last)
      }
    }

    const isMouseDown = ref(false)
    const handleMouseDown = () => {
      isMouseDown.value = true
    }

    const isSnackbarVisible = computed(() => uiStore.areInstructionsVisible)
    const showSnackbar = () => {
      if (isMouseDown.value) {
        // The audio player was clicked to open the single result view, not
        // focused via keyboard.
        isMouseDown.value = false
      } else {
        uiStore.showInstructionsSnackbar()
      }
    }
    const hideSnackbar = () => {
      uiStore.hideInstructionsSnackbar()
    }

    return {
      searchTerm,
      results,
      audioTrackSize,

      handleShiftTab,
      handleMouseDown,

      isSnackbarVisible,
      showSnackbar,
      hideSnackbar,
    }
  },
  head: {},
})
</script>
