<template>
  <div>
    <div
      v-if="!noResults"
      class="results-grid grid grid-cols-2 lg:grid-cols-5 2xl:grid-cols-6 gap-4 mb-4"
    >
      <VContentLink
        v-for="[mediaType, count] in resultCounts"
        :key="mediaType"
        :media-type="mediaType"
        :results-count="count"
        :to="localePath({ path: `/search/${mediaType}`, query: $route.query })"
        class="lg:col-span-2"
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

    <template v-if="isError" class="m-auto w-1/2 text-center pt-6">
      <h5>{{ errorHeader }}</h5>
      <p>{{ fetchState.fetchingError }}</p>
    </template>

    <VLoadMore
      v-if="canLoadMore && !fetchState.isFinished"
      class="mt-4"
      :is-fetching="resultsLoading"
      data-testid="load-more"
      @onLoadMore="onLoadMore"
    />
  </div>
</template>

<script>
import { computed, defineComponent, useContext } from '@nuxtjs/composition-api'

import { useMediaStore } from '~/stores/media'

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
  props: ['canLoadMore'],
  setup(_, { emit }) {
    const { i18n } = useContext()
    const mediaStore = useMediaStore()

    const onLoadMore = () => {
      emit('load-more')
    }

    /** @type {import('@nuxtjs/composition-api').ComputedRef<boolean>} */
    const resultsLoading = computed(() => {
      return (
        Boolean(mediaStore.fetchState.fetchingError) ||
        mediaStore.fetchState.isFetching
      )
    })

    /**
     * @type { ComputedRef<import('../../store/types').Media[]> }
     */
    const allMedia = computed(() => mediaStore.allMedia)

    const isError = computed(() => !!mediaStore.fetchState.fetchingError)

    /** @type {import('@nuxtjs/composition-api').ComputedRef<import('../../store/types').FetchState>} */
    const fetchState = computed(() => mediaStore.fetchState)

    const errorHeader = computed(() => {
      const type = i18n.t('browse-page.search-form.audio')
      return i18n.t('browse-page.fetching-error', { type })
    })

    const resultCounts = computed(() => mediaStore.resultCountsPerMediaType)

    const noResults = computed(
      () => fetchState.value.isFinished && allMedia.value.length === 0
    )

    return {
      isError,
      errorHeader,
      allMedia,
      onLoadMore,
      fetchState,
      resultsLoading,
      resultCounts,
      noResults,
    }
  },
})
</script>
