<template>
  <div>
    <div
      v-if="!noResults"
      class="results-grid mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0"
    >
      <VContentLink
        v-for="[mediaType, count] in resultCounts"
        :key="mediaType"
        :media-type="mediaType"
        :search-term="searchTerm"
        :results-count="count"
        :to="contentLinkPath(mediaType)"
      />
    </div>
    <VSnackbar size="large" :is-visible="isSnackbarVisible">
      <i18n path="allResults.snackbar.text" tag="p">
        <template #spacebar>
          <kbd class="font-sans">{{ $t(`allResults.snackbar.spacebar`) }}</kbd>
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
      :aria-label="
        $t('browsePage.aria.results', { query: searchTerm }).toString()
      "
    >
      <template v-for="item in allMedia">
        <VImageCell
          v-if="isDetail.image(item)"
          :key="item.id"
          :image="item"
          :search-term="searchTerm"
          aspect-ratio="square"
        />
        <VAudioResult
          v-if="isDetail.audio(item)"
          :key="item.id"
          :audio="item"
          :search-term="searchTerm"
          layout="box"
          :size="isSm ? 'l' : 's'"
          kind="search"
        />
      </template>
    </ol>

    <VLoadMore class="mb-6 mt-4 lg:mb-10" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "vue"
import { storeToRefs } from "pinia"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import { isDetail } from "~/types/media"

import { useI18n } from "~/composables/use-i18n"

import type { SupportedMediaType } from "~/constants/media"

import VSnackbar from "~/components/VSnackbar.vue"
import VImageCell from "~/components/VImageCell/VImageCell.vue"
import VAudioResult from "~/components/VSearchResultsGrid/VAudioResult.vue"
import VLoadMore from "~/components/VLoadMore.vue"
import VContentLink from "~/components/VContentLink/VContentLink.vue"
import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"

export default defineComponent({
  name: "VAllResultsGrid",
  components: {
    VSnackbar,
    VImageCell,
    VAudioResult,
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
        mediaStore.fetchState.isFetching ||
        !mediaStore.fetchState.hasStarted
      )
    })

    const contentLinkPath = (mediaType: SupportedMediaType) =>
      searchStore.getSearchPath({ type: mediaType })

    const allMedia = computed(() => mediaStore.allMedia)

    const isError = computed(() => !!mediaStore.fetchState.fetchingError)

    const fetchState = computed(() => mediaStore.fetchState)

    const errorHeader = computed(() => {
      const type = i18n.t("browsePage.searchForm.audio")
      return i18n.t("browsePage.fetchingError", { type })
    })

    const resultCounts = computed(() => mediaStore.resultCountsPerMediaType)

    const noResults = computed(
      () => fetchState.value.isFinished && allMedia.value.length === 0
    )

    const uiStore = useUiStore()
    const {
      areInstructionsVisible: isSnackbarVisible,
      isFilterVisible: isSidebarVisible,
    } = storeToRefs(uiStore)

    const isSm = computed(() => uiStore.isBreakpoint("sm"))

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
      isSm,

      isDetail,
    }
  },
})
</script>
