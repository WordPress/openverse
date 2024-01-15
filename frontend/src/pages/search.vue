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
      <NuxtPage
        :page-key="$route.path"
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

<script setup lang="ts">
import {
  createError,
  definePageMeta,
  isSearchTypeSupported,
  navigateTo,
  showError,
  useAsyncData,
  useHead,
  useNuxtApp,
  useRoute,
} from "#imports"

import { computed, ref, watch } from "vue"
import { watchDebounced } from "@vueuse/core"

import { storeToRefs } from "pinia"

import { searchMiddleware } from "~/middleware/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { ALL_MEDIA } from "~/constants/media"

import { skipToContentTargetId } from "~/constants/window"
import type { Results } from "~/types/result"
import { areQueriesEqual } from "~/utils/search-query-transform"
import { handledClientSide, isRetriable } from "~/utils/errors"

import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"

definePageMeta({
  layout: "search-layout",
  middleware: searchMiddleware,
})

const nuxtApp = useNuxtApp()

const featureFlagStore = useFeatureFlagStore()
const mediaStore = useMediaStore()
const searchStore = useSearchStore()

const route = useRoute()

const {
  searchTerm,
  searchType,
  apiSearchQueryParams: query,
  searchTypeIsSupported: supported,
} = storeToRefs(searchStore)

const { fetchState } = storeToRefs(mediaStore)

const pageTitle = ref(`${searchTerm.value} | Openverse`)
watch(searchTerm, () => {
  pageTitle.value = `${searchTerm.value} | Openverse`
})

useHead(() => ({
  title: pageTitle.value,
  meta: [{ hid: "robots", name: "robots", content: "all" }],
}))

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

const fetchMedia = async (payload: { shouldPersistMedia?: boolean } = {}) => {
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

  if (fetchingError.value === null || handledClientSide(fetchingError.value)) {
    return media
  }
  return fetchingError.value
}

const fetchingError = computed(() => fetchState.value.fetchingError)
const isFetching = computed(() => fetchState.value.isFetching)

/**
 * This watcher fires even when the queries are equal. We update the path only
 * when the queries change.
 */
watchDebounced(
  query,
  (newQuery, oldQuery) => {
    if (!areQueriesEqual(newQuery, oldQuery)) {
      navigateTo(searchStore.getSearchPath())
    }
  },
  { debounce: 800, maxWait: 5000 }
)

const routeQuery = computed(() => route.query)
const routePath = computed(() => route.path)
const shouldFetchSensitiveResults = computed(() => {
  return featureFlagStore.isOn("fetch_sensitive")
})

const handleLoadMore = async () => {
  await fetchMedia({ shouldPersistMedia: true })
}

await useAsyncData(
  "search",
  async () => {
    if (nuxtApp.isHydrating) {
      return searchResults.value
    }
    /**
     * By default, Nuxt only scrolls to top when the path changes.
     * This is a workaround to scroll to top when the query changes.
     */
    document.getElementById("main-page")?.scroll(0, 0)
    const res = await fetchMedia()
    if (!res || (res && "requestKind" in res)) {
      return showError(res ?? createError("No results found"))
    }
    return res
  },
  {
    server: false,
    lazy: true,
    watch: [shouldFetchSensitiveResults, routeQuery, routePath],
  }
)
</script>
