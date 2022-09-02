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
      @focus.native="showSnackbar"
    />
    <VLoadMore />
  </section>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  toRef,
  useMeta,
} from '@nuxtjs/composition-api'

import { useLoadMore } from '~/composables/use-load-more'
import { isMinScreen } from '~/composables/use-media-query'
import { useBrowserIsMobile } from '~/composables/use-browser-detection'
import { useFocusFilters } from '~/composables/use-focus-filters'
import { useI18n } from '~/composables/use-i18n'
import { Focus } from '~/utils/focus-management'

import { useUiStore } from '~/stores/ui'

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
    const i18n = useI18n()

    useMeta({ title: `${props.searchTerm} | Openverse` })

    const results = computed(() => props.resultItems.audio)

    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })

    // On SSR, we set the size to small if the User Agent is mobile, otherwise we set the size to medium.
    const isMobile = useBrowserIsMobile()
    const audioTrackSize = computed(() => {
      return !isMinScreenMd.value || isMobile
        ? 's'
        : props.isFilterVisible
        ? 'l'
        : 'm'
    })

    const isError = computed(() => !!props.fetchState.fetchingError)
    const errorHeader = computed(() => {
      const type = i18n.t('browse-page.search-form.audio')
      return i18n.t('browse-page.fetching-error', { type })
    })

    const focusFilters = useFocusFilters()
    const handleShiftTab = (event: KeyboardEvent, i: number) => {
      if (i === 0) {
        focusFilters.focusFilterSidebar(event, Focus.Last)
      }
    }
    const searchTermRef = toRef(props, 'searchTerm')
    const { canLoadMore, onLoadMore } = useLoadMore(searchTermRef)

    const uiStore = useUiStore()
    const isSnackbarVisible = computed(() => uiStore.areInstructionsVisible)
    const showSnackbar = () => {
      uiStore.showInstructionsSnackbar()
    }
    const hideSnackbar = () => {
      uiStore.hideInstructionsSnackbar()
    }

    return {
      results,
      audioTrackSize,
      isError,
      errorHeader,

      handleShiftTab,
      canLoadMore,
      onLoadMore,

      isSnackbarVisible,
      showSnackbar,
      hideSnackbar,
    }
  },
  head: {},
})
</script>
