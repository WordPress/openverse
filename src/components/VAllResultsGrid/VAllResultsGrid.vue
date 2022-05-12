<template>
  <div>
    <div
      v-if="!noResults"
      class="results-grid grid grid-cols-2 lg:grid-cols-5 2xl:grid-cols-6 gap-4 mb-4"
    >
      <VContentLink
        v-for="([mediaType, count], i) in resultCounts"
        :key="mediaType"
        :media-type="mediaType"
        :results-count="count"
        :to="localePath({ path: `/search/${mediaType}`, query: $route.query })"
        class="lg:col-span-2"
        @shift-tab="handleShiftTab($event, i)"
      />
    </div>
    <VGridSkeleton
      v-if="resultsLoading && allMedia.length === 0"
      is-for-tab="all"
    />
    <div
      v-else
      class="results-grid grid grid-cols-2 lg:grid-cols-5 2xl:grid-cols-6 gap-4"
    >
      <div v-for="item in allMedia" :key="item.id">
        <VImageCellSquare
          v-if="item.frontendMediaType === 'image'"
          :key="item.id"
          :image="item"
        />
        <VAudioCell
          v-if="item.frontendMediaType === 'audio'"
          :key="item.id"
          :audio="item"
        />
      </div>
    </div>

    <VLoadMore class="mt-4" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from '@nuxtjs/composition-api'

import { useMediaStore } from '~/stores/media'
import { useFocusFilters } from '~/composables/use-focus-filters'
import { Focus } from '~/utils/focus-management'

import { useI18n } from '~/composables/use-i18n'

import VImageCellSquare from '~/components/VAllResultsGrid/VImageCellSquare.vue'
import VAudioCell from '~/components/VAllResultsGrid/VAudioCell.vue'
import VLoadMore from '~/components/VLoadMore.vue'
import VContentLink from '~/components/VContentLink/VContentLink.vue'
import VGridSkeleton from '~/components/VSkeleton/VGridSkeleton.vue'

export default defineComponent({
  name: 'VAllResultsGrid',
  components: {
    VImageCellSquare,
    VAudioCell,
    VLoadMore,
    VGridSkeleton,
    VContentLink,
  },
  setup() {
    const i18n = useI18n()
    const mediaStore = useMediaStore()

    const resultsLoading = computed(() => {
      return (
        Boolean(mediaStore.fetchState.fetchingError) ||
        mediaStore.fetchState.isFetching
      )
    })

    const allMedia = computed(() => mediaStore.allMedia)

    const isError = computed(() => !!mediaStore.fetchState.fetchingError)

    const fetchState = computed(() => mediaStore.fetchState)

    const errorHeader = computed(() => {
      const type = i18n.t('browse-page.search-form.audio')
      return i18n.t('browse-page.fetching-error', { type })
    })

    const resultCounts = computed(() => mediaStore.resultCountsPerMediaType)

    const noResults = computed(
      () => fetchState.value.isFinished && allMedia.value.length === 0
    )
    const focusFilters = useFocusFilters()
    /**
     * Move focus to the filters sidebar if shift-tab is pressed on the first content link.
     * @param i - the index of the content link.
     * @param event - keydown event
     */
    const handleShiftTab = (event: KeyboardEvent, i: number) => {
      if (i === 0) {
        focusFilters.focusFilterSidebar(event, Focus.Last)
      }
    }

    return {
      isError,
      errorHeader,
      allMedia,
      fetchState,
      resultsLoading,
      resultCounts,
      noResults,
      handleShiftTab,
    }
  },
})
</script>
