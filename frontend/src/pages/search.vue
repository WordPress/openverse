<template>
  <VSkipToContentContainer
    class="browse-page flex w-full flex-col px-6 lg:px-10"
  >
    <VSearchGrid
      ref="searchGridRef"
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
  </VSkipToContentContainer>
</template>

<script lang="ts">
import { isShallowEqualObjects } from "@wordpress/is-shallow-equal"
import { computed, inject, ref } from "vue"
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { IsSidebarVisibleKey } from "~/types/provides"

import VSearchGrid from "~/components/VSearchGrid.vue"
import VSkipToContentContainer from "~/components/VSkipToContentContainer.vue"
import VScrollButton from "~/components/VScrollButton.vue"

import type { Context } from "@nuxt/types"

export default defineComponent({
  name: "BrowsePage",
  components: {
    VScrollButton,
    VSearchGrid,
    VSkipToContentContainer,
  },
  beforeRouteEnter(to, from, next) {
    /**
     * The order in which beforeRouteEnter and middleware are called is indeterminate.
     * We need to make sure that query `q` exists before checking if it matches
     * the store searchTerm.
     */
    const searchStore = useSearchStore()
    if (to.query.q && to.query.q !== searchStore.searchTerm) {
      searchStore.setSearchTerm(to.query.q)
    }
    next()
  },
  layout: "content-layout",
  middleware({ route, redirect }) {
    /**
     * This anonymous middleware redirects any search without a query to the homepage.
     * This is meant to block direct access to /search and all sub-routes, with
     * an exception for the 'creator' filter. The creator filter doesn't send
     * the search query to the API.
     */
    if (!route.query.q && !route.query.searchBy) return redirect("/")
  },
  scrollToTop: false,
  setup() {
    const searchGridRef = ref<InstanceType<typeof VSearchGrid> | null>(null)

    const showScrollButton = inject("showScrollButton")
    const isSidebarVisible = inject(IsSidebarVisibleKey)
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    // I don't know *exactly* why this is necessary, but without it
    // transitioning from the homepage to this page breaks the
    // watcher in useStorage and recent searches won't be saved
    // properly. It is something related to Pinia, Nuxt SSR,
    // hydration and Vue reactives. Hopefully fixed in Nuxt 3.
    searchStore.refreshRecentSearches()

    const searchTerm = computed(() => searchStore.searchTerm)
    const searchType = computed(() => searchStore.searchType)
    const query = computed(() => searchStore.searchQueryParams)
    const supported = computed(() => searchStore.searchTypeIsSupported)
    const resultCount = computed(() => mediaStore.resultCount)
    const fetchState = computed(() => mediaStore.fetchState)
    const resultItems = computed(() => mediaStore.resultItems)

    const needsFetching = computed(() =>
      Boolean(
        searchStore.searchTypeIsSupported &&
          !mediaStore.resultCount &&
          searchStore.searchTerm.trim() !== ""
      )
    )

    useMeta({
      title: `${searchTerm.value} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    return {
      searchGridRef,
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
  watch: {
    /**
     * Updates the search type only if the route's path changes.
     */
    async $route(newRoute: Context["route"], oldRoute: Context["route"]) {
      if (
        newRoute.path !== oldRoute.path ||
        !isShallowEqualObjects(newRoute.query, oldRoute.query)
      ) {
        const { query, path } = newRoute
        const searchStore = useSearchStore(this.$nuxt.$pinia)
        searchStore.setSearchStateFromUrl({ urlQuery: query, path })
        await this.fetchMedia()
      }
    },
  },
  methods: {
    fetchMedia(payload: { shouldPersistMedia?: boolean } = {}) {
      const mediaStore = useMediaStore(this.$pinia)
      return mediaStore.fetchMedia(payload)
    },
  },
})
</script>
