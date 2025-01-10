<script setup lang="ts">
import {
  definePageMeta,
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

import { skipToContentTargetId } from "#shared/constants/window"
import { areQueriesEqual } from "#shared/utils/search-query-transform"
import { handledClientSide, isRetriable } from "#shared/utils/errors"
import type { Results } from "#shared/types/result"
import { searchMiddleware } from "~/middleware/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useMediaStore } from "~/stores/media"
import { isSearchTypeSupported, useSearchStore } from "~/stores/search"

import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"

defineOptions({
  name: "SearchPage",
})

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
} = storeToRefs(searchStore)

const fetchingError = computed(() => mediaStore.fetchState.error)
const isFetching = computed(() => mediaStore.isFetching)

const pageTitle = ref(`${searchTerm.value} | Openverse`)
watch(searchTerm, () => {
  pageTitle.value = `${searchTerm.value} | Openverse`
})

useHead(() => ({
  title: pageTitle.value,
}))

const searchResults = ref<Results | null>(
  isSearchTypeSupported(searchType.value) ? mediaStore.searchResults : null
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
    mediaStore.fetchState.status !== "idle" &&
    fetchingError.value !== null &&
    !isRetriable(fetchingError.value)
  if (shouldNotRefetch) {
    return
  }
  if (!payload.shouldPersistMedia) {
    searchResults.value = { type: searchType.value, items: [] }
  }

  const media = await mediaStore.fetchMedia(payload)

  if (!fetchingError.value || handledClientSide(fetchingError.value)) {
    searchResults.value = media
    return media
  }
  return fetchingError.value
}

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

    const error = !res
      ? (fetchingError.value ?? "Fetch media error") // middleware in SSR returned an error
      : "requestKind" in res // fetchMedia returned a `FetchingError`
        ? res
        : null
    if (error) {
      return showError(error)
    }
    return res
  },
  {
    server: false,
    watch: [shouldFetchSensitiveResults, routeQuery, routePath],
  }
)
</script>

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
    <div v-else>
      <NuxtPage
        :page-key="$route.path"
        :results="searchResults"
        :is-fetching="isFetching"
        :search-term="searchTerm"
        :handle-load-more="handleLoadMore"
        data-testid="search-results"
      />
    </div>
  </div>
</template>
