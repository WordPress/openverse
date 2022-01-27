<template>
  <div>
    <div
      v-if="!noResults"
      class="results-grid grid grid-cols-2 lg:grid-cols-5 2xl:grid-cols-6 gap-4 mb-4"
    >
      <NuxtLink
        v-for="[key, item] in results"
        :key="key"
        :to="{ path: `/search/${key}`, query: $route.query }"
        class="lg:col-span-2 hover:no-underline"
      >
        <VContentLink :results-count="item.count" :media-type="key" />
      </NuxtLink>
    </div>
    <GridSkeleton
      v-if="resultsLoading && allMedia.length === 0"
      is-for-tab="all"
    />
    <div
      v-else
      class="results-grid grid grid-cols-2 lg:grid-cols-5 2xl:grid-cols-6 gap-4"
    >
      <div v-for="item in allMedia" :key="item.id">
        <VImageCell
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

import VImageCell from '~/components/VAllResultsGrid/VImageCell.vue'
import VAudioCell from '~/components/VAllResultsGrid/VAudioCell.vue'
import VLoadMore from '~/components/VLoadMore.vue'

import srand from '~/utils/srand'

export default defineComponent({
  name: 'VAllResultsGrid',
  components: { VImageCell, VAudioCell, VLoadMore },
  props: ['canLoadMore'],
  setup(_, { emit }) {
    const { i18n, store } = useContext()

    const onLoadMore = () => {
      emit('load-more')
    }

    /** @type {import('@nuxtjs/composition-api').ComputedRef<boolean>} */
    const resultsLoading = computed(() => {
      return (
        Boolean(store.getters['media/fetchState'].fetchingError) ||
        store.getters['media/fetchState'].isFetching
      )
    })

    /**
     *
     * @type { ComputedRef<import('../../store/types').AudioDetail[] | import('../../store/types').ImageDetail[]> }
     */
    const allMedia = computed(() => {
      // if (resultsLoading.value) return []
      const media = store.getters['media/mediaResults']
      const mediaKeys = Object.keys(media)

      // Seed the random number generator with the ID of
      // the first and last search result, so the non-image
      // distribution is the same on repeated searches
      const rand = srand(Object.keys(media[mediaKeys[0]])[0])
      const randomIntegerInRange = (min, max) =>
        Math.floor(rand() * (max - min + 1)) + min

      /** @type {import('../../store/types').AudioDetail[] | import('../../store/types').ImageDetail[]} */
      const newResults = []
      // first push all images to the results list
      for (const id of Object.keys(media['image'])) {
        const item = media['image'][id]
        item.frontendMediaType = 'image'
        newResults.push(item)
      }

      // push other items into the list, using a random index.
      let nonImageIndex = 1
      for (const type of Object.keys(media).slice(1)) {
        for (const id of Object.keys(media[type])) {
          const item = media[type][id]
          item.frontendMediaType = type
          newResults.splice(nonImageIndex, 0, item)
          if (nonImageIndex > newResults.length + 1) break
          nonImageIndex = randomIntegerInRange(
            nonImageIndex + 1,
            nonImageIndex + 6
          )
        }
      }

      return newResults
    })

    const isError = computed(
      () => !!store.getters['media/fetchState'].fetchingError
    )

    /** @type {import('@nuxtjs/composition-api').ComputedRef<import('../../store/types').FetchState>} */
    const fetchState = computed(() => {
      return store.getters['media/fetchState']
    })

    const errorHeader = computed(() => {
      const type = i18n.t('browse-page.search-form.audio')
      return i18n.t('browse-page.fetching-error', { type })
    })

    const results = computed(() => {
      return Object.entries(store.getters['media/results'])
    })

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
      results,
      noResults,
    }
  },
})
</script>
