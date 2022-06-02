<template>
  <section>
    <VGridSkeleton
      v-if="results.length === 0 && !fetchState.isFinished"
      is-for-tab="audio"
    />
    <VAudioTrack
      v-for="(audio, i) in results"
      :key="audio.id"
      class="mb-8 md:mb-10"
      :audio="audio"
      :size="audioTrackSize"
      layout="row"
      @shift-tab="handleShiftTab($event, i)"
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

import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'
import VLoadMore from '~/components/VLoadMore.vue'
import VGridSkeleton from '~/components/VSkeleton/VGridSkeleton.vue'

import { propTypes } from './search-page.types'

export default defineComponent({
  name: 'AudioSearch',
  components: {
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

    return {
      results,
      audioTrackSize,
      isError,
      errorHeader,

      handleShiftTab,
      canLoadMore,
      onLoadMore,
    }
  },
  head: {},
})
</script>
