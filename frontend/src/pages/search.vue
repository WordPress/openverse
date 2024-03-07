<template>
  <div
    :id="skipToContentTargetId"
    tabindex="-1"
    class="browse-page flex w-full flex-col px-6 lg:px-10"
  >
    <VErrorSection
      v-if="fetchingError"
      :fetching-error="fetchingError"
      class="w-full py-10"
    />
    <section v-else>
      <NuxtChild
        :key="$route.path"
        :results="searchResults"
        :is-fetching="isFetching"
        :search-term="searchTerm"
        :supported="supported"
        :handle-load-more="handleLoadMore"
        data-testid="search-results"
      />
    </section>
  </div>
</template>

<script lang="ts">
import { isShallowEqualObjects } from "@wordpress/is-shallow-equal"
import { computed, ref, watch } from "vue"
import { watchDebounced } from "@vueuse/core"
import { storeToRefs } from "pinia"
import {
  defineComponent,
  useContext,
  useFetch,
  useMeta,
  useRoute,
  useRouter,
} from "@nuxtjs/composition-api"

import { searchMiddleware } from "~/middleware/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useMediaStore } from "~/stores/media"
import { isSearchTypeSupported, useSearchStore } from "~/stores/search"
import { ALL_MEDIA } from "~/constants/media"

import { skipToContentTargetId } from "~/constants/window"
import type { Results } from "~/types/result"
import { areQueriesEqual } from "~/utils/search-query-transform"
import { handledClientSide, isRetriable } from "~/utils/errors"

import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"

export default defineComponent({
  name: "BrowsePage",
  components: {
    VErrorSection,
  },
  layout: "search-layout",
  middleware: searchMiddleware,
  fetchOnServer: false,
  setup() {
    const featureFlagStore = useFeatureFlagStore()
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const route = useRoute()
    const router = useRouter()

    // I don't know *exactly* why this is necessary, but without it
    // transitioning from the homepage to this page breaks the
    // watcher in useStorage and recent searches won't be saved
    // properly. It is something related to Pinia, Nuxt SSR,
    // hydration and Vue reactives. Hopefully fixed in Nuxt 3.
    searchStore.refreshRecentSearches()

    const {
      searchTerm,
      searchType,
      apiSearchQueryParams: query,
      searchTypeIsSupported: supported,
    } = storeToRefs(searchStore)

    const { resultCount, fetchState } = storeToRefs(mediaStore)

    const needsFetching = computed(() =>
      Boolean(supported.value && !resultCount.value && searchTerm.value !== "")
    )

    const pageTitle = ref(`${searchTerm.value} | Openverse`)
    watch(searchTerm, () => {
      pageTitle.value = `${searchTerm.value} | Openverse`
    })

    useMeta(() => ({
      title: pageTitle.value,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    }))

    const { error: nuxtError } = useContext()

    const searchResults = ref<Results | null>(
      isSearchTypeSupported(searchType.value)
        ? ({
            type: searchType.value,
            items:
              searchType.value === ALL_MEDIA
                ? mediaStore.allMedia
                : mediaStore.resultItems[searchType.value],
          } as Results)
        : null
    )

    const fetchMedia = async (
      payload: { shouldPersistMedia?: boolean } = {}
    ) => {
      if (!isSearchTypeSupported(searchType.value)) {
        return
      }
      /**
       * If the fetch has already started in the middleware,
       * and there is an error status that will not change if retried, don't re-fetch.
       */
      const shouldNotRefetch =
        fetchState.value.hasStarted &&
        fetchingError.value !== null &&
        !isRetriable(fetchingError.value)
      if (shouldNotRefetch) {
        return
      }
      if (!payload.shouldPersistMedia) {
        searchResults.value = { type: searchType.value, items: [] }
      }

      const media = await mediaStore.fetchMedia(payload)
      searchResults.value = { type: searchType.value, items: media } as Results

      if (
        fetchingError.value === null ||
        handledClientSide(fetchingError.value)
      ) {
        return null
      }
      return nuxtError(fetchingError.value)
    }

    const fetchingError = computed(() => fetchState.value.fetchingError)
    const isFetching = computed(() => fetchState.value.isFetching)

    /**
     * Search middleware runs when the path changes. This watcher
     * is necessary to handle the query changes.
     *
     * It updates the search store state from the URL query,
     * fetches media, and scrolls to top if necessary.
     */
    watch(route, async (newRoute, oldRoute) => {
      if (
        newRoute.path !== oldRoute.path ||
        !isShallowEqualObjects(newRoute.query, oldRoute.query)
      ) {
        const { query: urlQuery, path } = newRoute
        searchStore.setSearchStateFromUrl({ urlQuery, path })

        const mediaStore = useMediaStore()
        mediaStore.clearMedia()

        /**
         * By default, Nuxt only scrolls to top when the path changes.
         * This is a workaround to scroll to top when the query changes.
         */
        document.getElementById("main-page")?.scroll(0, 0)
        await fetchMedia()
      }
    })

    /**
     * This watcher fires even when the queries are equal. We update the path only
     * when the queries change.
     */
    watchDebounced(
      query,
      (newQuery, oldQuery) => {
        if (!areQueriesEqual(newQuery, oldQuery)) {
          router.push(searchStore.getSearchPath())
        }
      },
      { debounce: 800, maxWait: 5000 }
    )

    const shouldFetchSensitiveResults = computed(() => {
      return featureFlagStore.isOn("fetch_sensitive")
    })
    watch(shouldFetchSensitiveResults, async () => {
      await fetchMedia()
    })

    useFetch(async () => {
      if (needsFetching.value) {
        await fetchMedia()
      }
    })
    const handleLoadMore = async () => {
      await fetchMedia({ shouldPersistMedia: true })
    }

    return {
      searchTerm,
      searchType,
      supported,
      query,

      resultCount,
      searchResults,
      isFetching,
      fetchingError,

      handleLoadMore,

      skipToContentTargetId,
    }
  },
  head: {},
})
</script>
