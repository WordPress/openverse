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
          :result-items="resultItems"
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
import { defineComponent, useMeta, useRoute } from "@nuxtjs/composition-api"

import { searchMiddleware } from "~/middleware/search"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
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
      Boolean(
        supported.value && !resultCount.value && searchTerm.value.trim() !== ""
      )
    )

    useMeta({
      title: `${searchTerm.value} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    const fetchMedia = async (
      payload: { shouldPersistMedia?: boolean } = {}
    ) => {
      return mediaStore.fetchMedia(payload)
    }

    watch(route, async (newRoute, oldRoute) => {
      /**
       * Updates the search type only if the route's path changes.
       * Scrolls `main-page` to top if the path changes.
       */
      if (
        newRoute.path !== oldRoute.path ||
        !isShallowEqualObjects(newRoute.query, oldRoute.query)
      ) {
        const { query: urlQuery, path } = newRoute
        searchStore.setSearchStateFromUrl({ urlQuery, path })

        document.getElementById("main-page")?.scroll(0, 0)
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

      fetchMedia,
    }
  },
  /**
   * asyncData blocks the rendering of the page, so we only
   * update the state from the route here, and do not fetch media.
   */
  async asyncData({ route, $pinia }) {
    const searchStore = useSearchStore($pinia)
    await searchStore.initProviderFilters()
    searchStore.setSearchStateFromUrl({
      path: route.path,
      urlQuery: route.query,
    })
  },
  /**
   * Fetch media, if necessary, in a non-blocking way.
   */
  async fetch() {
    if (this.needsFetching) {
      await this.fetchMedia()
    }
  },
  head: {},
})
</script>
