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
  watch,
  toRef,
} from '@nuxtjs/composition-api'

import { useBrowserIsMobile } from '~/composables/use-browser-detection'
import { useFocusFilters } from '~/composables/use-focus-filters'
import { Focus } from '~/utils/focus-management'

import { useUiStore } from '~/stores/ui'

import { IsMinScreenMdKey } from '~/types/provides'

import VSnackbar from '~/components/VSnackbar.vue'
import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'
import VLoadMore from '~/components/VLoadMore.vue'
import VGridSkeleton from '~/components/VSkeleton/VGridSkeleton.vue'

import { propTypes } from './search-page.types'

export default defineComponent({
  name: 'AudioSearch',
  components: {
    VSnackbar,
    VAudioTrack,
    VGridSkeleton,
    VLoadMore,
  },
  props: propTypes,
  setup(props) {
    useMeta({ title: `${props.searchTerm} | Openverse` })

    const results = computed(() => props.resultItems.audio)

    const isMinScreenMd = inject(IsMinScreenMdKey)
    const filterVisibleRef = toRef(props, 'isFilterVisible')

    // On SSR, we set the size to small if the User Agent is mobile, otherwise we set the size to medium.
    const isMobile = useBrowserIsMobile()
    const audioTrackSize = ref(
      !isMinScreenMd.value || isMobile ? 's' : props.isFilterVisible ? 'l' : 'm'
    )

    watch([filterVisibleRef, isMinScreenMd], ([filterVisible, isMd]) => {
      if (!isMd) {
        audioTrackSize.value = 's'
      } else {
        audioTrackSize.value = filterVisible ? 'l' : 'm'
      }
    })

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

    const uiStore = useUiStore()
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
