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
      <header v-if="query.q && supported" class="my-0 md:mb-8 md:mt-4">
        <VSearchResultsTitle :size="isAllView ? 'large' : 'default'">{{
          searchTerm
        }}</VSearchResultsTitle>
      </header>
      <NuxtPage
        :key="$route.path"
        :search-term="searchTerm"
        :supported="supported"
        data-testid="search-results"
      />
      <VExternalSearchForm
        v-if="!isAllView"
        :search-term="searchTerm"
        :is-supported="supported"
        :has-no-results="false"
      />
      <VScrollButton
        v-show="showScrollButton"
        :is-filter-sidebar-visible="isSidebarVisible"
        data-testid="scroll-button"
      />
    </section>
  </div>
</template>

<script lang="ts">
import {
  defineNuxtComponent,
  definePageMeta,
  navigateTo,
  showError,
  useAsyncData,
  useHead,
} from "#imports"

import { computed, inject, ref, watch } from "vue"
import { watchDebounced } from "@vueuse/core"
import { storeToRefs } from "pinia"

import { searchMiddleware } from "~/middleware/search"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { ALL_MEDIA, isSupportedMediaType } from "~/constants/media"

import { skipToContentTargetId } from "~/constants/window"
import { IsSidebarVisibleKey, ShowScrollButtonKey } from "~/types/provides"
import { areQueriesEqual } from "~/utils/search-query-transform"
import { isRetriable } from "~/utils/errors"

import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"
import VScrollButton from "~/components/VScrollButton.vue"
import VExternalSearchForm from "~/components/VExternalSearch/VExternalSearchForm.vue"
import VSearchResultsTitle from "~/components/VSearchResultsTitle.vue"

export default defineNuxtComponent({
  name: "BrowsePage",
  components: {
    VErrorSection,
    VSearchResultsTitle,
    VExternalSearchForm,
    VScrollButton,
  },
  setup() {
    definePageMeta({ layout: "search-layout", middleware: searchMiddleware })
    const showScrollButton = inject(ShowScrollButtonKey)
    const isSidebarVisible = inject(IsSidebarVisibleKey)
    const featureFlagStore = useFeatureFlagStore()
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

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

    const isAllView = computed(() => searchType.value === ALL_MEDIA)

    const needsFetching = computed(() =>
      Boolean(supported.value && !resultCount.value && searchTerm.value !== "")
    )

    const pageTitle = ref(`${searchTerm.value} | Openverse`)
    watch(searchTerm, () => {
      pageTitle.value = `${searchTerm.value} | Openverse`
    })

    useHead(() => ({
      title: pageTitle.value,
      meta: [{ name: "robots", content: "all" }],
    }))

    const fetchMedia = async (
      payload: { shouldPersistMedia?: boolean } = {}
    ) => {
      /**
       * If the fetch has already started in the middleware,
       * and there is an error status that will not change if retried, don't re-fetch.
       */
      const shouldNotRefetch =
        mediaStore.fetchState.hasStarted &&
        fetchingError.value !== null &&
        !isRetriable(fetchingError.value)
      if (shouldNotRefetch) {
        return
      }

      try {
        await mediaStore.fetchMedia(payload)
      } catch (error) {
        return showError(mediaStore.fetchState.fetchingError ?? {})
      }
    }

    const fetchingError = computed(() => mediaStore.fetchState.fetchingError)

    /**
     * This watcher fires even when the queries are equal. We update the path only
     * when the queries change.
     */
    watchDebounced(
      query,
      (newQuery, oldQuery) => {
        if (!areQueriesEqual(newQuery, oldQuery)) {
          mediaStore.clearMedia()
          /**
           * By default, Nuxt only scrolls to top when the path changes.
           * This is a workaround to scroll to top when the query changes.
           */
          document.getElementById("main-page")?.scroll(0, 0)
          const path = searchStore.getSearchPath()
          return Promise.allSettled([navigateTo(path), fetchMedia()])
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

    useAsyncData(
      "search",
      async () => {
        if (needsFetching.value) {
          await fetchMedia()
        }
      },
      {
        server: false,
        watch: [shouldFetchSensitiveResults, searchTerm, searchType],
      }
    )

    return {
      showScrollButton,
      searchTerm,
      searchType,
      supported,
      query,
      isSupportedMediaType,

      resultCount,
      fetchState,
      needsFetching,
      isSidebarVisible,
      fetchingError,

      isAllView,

      skipToContentTargetId,
    }
  },
})
</script>
