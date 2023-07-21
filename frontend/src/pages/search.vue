<template>
  <div
    :id="skipToContentTargetId"
    tabindex="-1"
    class="browse-page flex w-full flex-col px-6 lg:px-10"
  >
    <VSearchGrid
      :fetch-state="fetchState"
      :query="query"
      :supported="supported"
      :search-type="searchType"
      :results-count="resultCount"
      data-testid="search-grid"
    >
      <template #media>
        <NuxtChild
          :key="$route.path"
          :results="resultItems[searchType]"
          :fetch-state="fetchState"
          :search-term="query.q"
          :supported="supported"
          data-testid="search-results"
        />
      </template>
    </VSearchGrid>
    <VScrollButton
      v-show="showScrollButton"
      :is-filter-sidebar-visible="isSidebarVisible"
      data-testid="scroll-button"
    />
  </div>
</template>

<script lang="ts">
import { isShallowEqualObjects } from "@wordpress/is-shallow-equal"
import { computed, inject, watch } from "vue"
import { storeToRefs } from "pinia"
import {
  defineComponent,
  useContext,
  useFetch,
  useMeta,
  useRoute,
} from "@nuxtjs/composition-api"

import { searchMiddleware } from "~/middleware/search"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { NO_RESULT } from "~/constants/errors"
import { skipToContentTargetId } from "~/constants/window"
import { IsSidebarVisibleKey, ShowScrollButtonKey } from "~/types/provides"

import VSearchGrid from "~/components/VSearchGrid.vue"
import VScrollButton from "~/components/VScrollButton.vue"

export default defineComponent({
  name: "BrowsePage",
  components: {
    VScrollButton,
    VSearchGrid,
  },
  layout: "search-layout",
  middleware: searchMiddleware,
  fetchOnServer: false,
  setup() {
    const showScrollButton = inject(ShowScrollButtonKey)
    const isSidebarVisible = inject(IsSidebarVisibleKey)
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const route = useRoute()

    // I don't know *exactly* why this is necessary, but without it
    // transitioning from the homepage to this page breaks the
    // watcher in useStorage and recent searches won't be saved
    // properly. It is something related to Pinia, Nuxt SSR,
    // hydration and Vue reactives. Hopefully fixed in Nuxt 3.
    searchStore.refreshRecentSearches()

    const {
      searchTerm,
      searchType,
      searchQueryParams: query,
      searchTypeIsSupported: supported,
    } = storeToRefs(searchStore)

    const { resultCount, fetchState, resultItems } = storeToRefs(mediaStore)

    const needsFetching = computed(() =>
      Boolean(supported.value && !resultCount.value && searchTerm.value !== "")
    )

    useMeta({
      title: `${searchTerm.value} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    const { error: nuxtError } = useContext()

    const fetchMedia = async (
      payload: { shouldPersistMedia?: boolean } = {}
    ) => {
      /**
       * If the fetch has already started in the middleware,
       * and there is an error or no results were found, don't re-fetch.
       */
      const shouldNotRefetch =
        mediaStore.fetchState.fetchingError?.message &&
        mediaStore.fetchState.hasStarted
      if (shouldNotRefetch) return

      const results = await mediaStore.fetchMedia(payload)
      if (!results) {
        const error = mediaStore.fetchState.fetchingError
        /**
         * NO_RESULT error is handled by the VErrorSection component in the child pages.
         * For all other errors, show the Nuxt error page.
         */
        if (error?.statusCode && !error?.message.includes(NO_RESULT))
          return nuxtError(mediaStore.fetchState.fetchingError)
      }
    }

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

        /**
         * By default, Nuxt only scrolls to top when the path changes.
         * This is a workaround to scroll to top when the query changes.
         */
        document.getElementById("main-page")?.scroll(0, 0)
        await fetchMedia()
      }
    })

    useFetch(async () => {
      if (needsFetching.value) {
        await fetchMedia()
      }
    })

    return {
      showScrollButton,
      searchTerm,
      searchType,
      supported,
      query,

      resultCount,
      fetchState,
      resultItems,
      needsFetching,
      isSidebarVisible,

      skipToContentTargetId,
    }
  },
  head: {},
})
</script>
