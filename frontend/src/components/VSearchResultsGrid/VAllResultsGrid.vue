<template>
  <div>
    <div v-if="!noResults" class="results-grid mb-4 grid grid-cols-2 gap-4">
      <VContentLink
        v-for="[mediaType, count] in resultCounts"
        :key="mediaType"
        :media-type="mediaType"
        :results-count="count"
        :to="contentLinkPath(mediaType)"
      />
    </div>
    <VSnackbar size="large" :is-visible="isSnackbarVisible">
      <i18n path="all-results.snackbar.text" tag="p">
        <template #spacebar>
          <kbd class="font-sans">{{ $t(`all-results.snackbar.spacebar`) }}</kbd>
        </template>
      </i18n>
    </VSnackbar>
    <VGridSkeleton
      v-if="resultsLoading && allMedia.length === 0"
      is-for-tab="all"
    />
    <ol
      v-else
      class="results-grid grid grid-cols-2 gap-4"
      :class="
        isSidebarVisible
          ? 'lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5'
          : 'sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6'
      "
      :aria-label="$t('browse-page.aria.results', { query: searchTerm })"
    >
      <li v-for="item in allMedia" :key="item.id">
        <VImageCell
          v-if="isDetail.image(item)"
          :key="item.id"
          :image="item"
          :search-term="searchTerm"
          aspect-ratio="square"
        />
        <VAudioCell
          v-if="isDetail.audio(item)"
          :key="item.id"
          :audio="item"
          :search-term="searchTerm"
          @interacted="hideSnackbar"
          @focus.native="showSnackbar"
        />
      </li>
    </ol>

    <VLoadMore class="mt-4" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "vue"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import { isDetail } from "~/types/media"

import { useI18n } from "~/composables/use-i18n"

import VSnackbar from "~/components/VSnackbar.vue"
import VImageCell from "~/components/VSearchResultsGrid/VImageCell.vue"
import VAudioCell from "~/components/VSearchResultsGrid/VAudioCell.vue"
import VLoadMore from "~/components/VLoadMore.vue"
import VContentLink from "~/components/VContentLink/VContentLink.vue"
import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"

export default defineComponent({
  name: "VAllResultsGrid",
  components: {
    VSnackbar,
    VImageCell,
    VAudioCell,
    VLoadMore,
    VGridSkeleton,
    VContentLink,
  },
  setup() {
    const i18n = useI18n()
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const searchTerm = computed(() => searchStore.searchTerm)

    const resultsLoading = computed(() => {
      return (
        Boolean(mediaStore.fetchState.fetchingError) ||
        mediaStore.fetchState.isFetching
      )
    })

    const contentLinkPath = (mediaType: string) =>
      searchStore.getSearchPath({ type: mediaType })

    const allMedia = computed(() => mediaStore.allMedia)

    const isError = computed(() => !!mediaStore.fetchState.fetchingError)

    const fetchState = computed(() => mediaStore.fetchState)

    const errorHeader = computed(() => {
      const type = i18n.t("browse-page.search-form.audio")
      return i18n.t("browse-page.fetching-error", { type })
    })

    const resultCounts = computed(() => mediaStore.resultCountsPerMediaType)

    const noResults = computed(
      () => fetchState.value.isFinished && allMedia.value.length === 0
    )

    const uiStore = useUiStore()
    const isSnackbarVisible = computed(() => uiStore.areInstructionsVisible)
    const showSnackbar = () => {
      uiStore.showInstructionsSnackbar()
    }
    const hideSnackbar = () => {
      uiStore.hideInstructionsSnackbar()
    }

    const isSidebarVisible = computed(() => uiStore.isFilterVisible)

    return {
      searchTerm,
      isError,
      errorHeader,
      allMedia,
      fetchState,
      resultsLoading,
      resultCounts,
      noResults,

      contentLinkPath,

      isSidebarVisible,

      isSnackbarVisible,
      showSnackbar,
      hideSnackbar,

      isDetail,
    }
  },
})
</script>
