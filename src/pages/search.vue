<template>
  <VSkipToContentContainer
    class="browse-page flex flex-col px-4 md:px-10 w-full"
  >
    <VSearchGrid
      ref="searchGridRef"
      :fetch-state="fetchState"
      :query="query"
      :supported="supported"
      :search-type="searchType"
      :results-count="resultCount"
      data-testid="search-grid"
      @tab="handleTab($event, 'search-grid')"
    >
      <template #media>
        <NuxtChild
          :key="$route.path"
          :result-items="resultItems"
          :fetch-state="fetchState"
          :is-filter-visible="isFilterSidebarVisible"
          :search-term="query.q"
          :supported="supported"
          data-testid="search-results"
        />
      </template>
    </VSearchGrid>
    <VScrollButton
      v-show="showScrollButton"
      data-testid="scroll-button"
      @tab="handleTab($event, 'scroll-button')"
    />
  </VSkipToContentContainer>
</template>

<script lang="ts">
import { isShallowEqualObjects } from '@wordpress/is-shallow-equal'
import { computed, defineComponent, inject, ref } from '@nuxtjs/composition-api'

import { isMinScreen } from '~/composables/use-media-query'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'
import { Focus, focusIn } from '~/utils/focus-management'
import { useMediaStore } from '~/stores/media'
import { useSearchStore } from '~/stores/search'

import VSearchGrid from '~/components/VSearchGrid.vue'
import VSkipToContentContainer from '~/components/VSkipToContentContainer.vue'
import VScrollButton from '~/components/VScrollButton.vue'

export default defineComponent({
  name: 'BrowsePage',
  components: {
    VScrollButton,
    VSearchGrid,
    VSkipToContentContainer,
  },
  scrollToTop: false,
  setup() {
    const searchGridRef = ref(null)
    const isMinScreenMd = isMinScreen('md')
    const { isVisible: isFilterSidebarVisible } = useFilterSidebarVisibility()
    const showScrollButton = inject('showScrollButton')
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const searchTerm = computed(() => searchStore.searchTerm)
    const searchType = computed(() => searchStore.searchType)
    const query = computed(() => searchStore.searchQueryParams)
    const supported = computed(() => searchStore.searchTypeIsSupported)
    const resultCount = computed(() => mediaStore.resultCount)
    const fetchState = computed(() => mediaStore.fetchState)
    const resultItems = computed(() => mediaStore.resultItems)

    const handleTab = (event: KeyboardEvent, element: string) => {
      if (showScrollButton.value && element !== 'scroll-button') {
        return
      }
      focusIn(document.getElementById('__layout'), Focus.First)
    }
    return {
      searchGridRef,
      isMinScreenMd,
      isFilterSidebarVisible,
      showScrollButton,
      searchTerm,
      searchType,
      supported,
      query,

      resultCount,
      fetchState,
      resultItems,
      fetchMedia: mediaStore.fetchMedia,
      setSearchStateFromUrl: searchStore.setSearchStateFromUrl,
      handleTab,
    }
  },
  async asyncData({ route, $pinia }) {
    const searchStore = useSearchStore($pinia)
    const mediaStore = useMediaStore($pinia)
    searchStore.setSearchStateFromUrl({
      path: route.path,
      urlQuery: route.query,
    })
    if (
      searchStore.searchTypeIsSupported &&
      !mediaStore.resultCount &&
      searchStore.searchTerm.trim() !== ''
    ) {
      await mediaStore.fetchMedia()
    }
  },
  watch: {
    /**
     * Updates the search type only if the route's path changes.
     * @param {import('@nuxt/types').Context['route']} newRoute
     * @param {import('@nuxt/types').Context['route']} oldRoute
     */
    async $route(newRoute, oldRoute) {
      if (
        newRoute.path !== oldRoute.path ||
        !isShallowEqualObjects(newRoute.query, oldRoute.query)
      ) {
        const { query, path } = newRoute
        await this.setSearchStateFromUrl({ urlQuery: query, path })
        this.fetchMedia()
      }
    },
  },
})
</script>
