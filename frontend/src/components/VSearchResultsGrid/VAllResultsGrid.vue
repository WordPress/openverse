<template>
  <div>
    <div class="results-grid mb-4 mt-2 grid grid-cols-2 gap-4 md:mt-0">
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
      <i18n-t scope="global" keypath="allResults.snackbar.text" tag="p">
        <template #spacebar>
          <kbd class="font-sans">{{ t(`allResults.snackbar.spacebar`) }}</kbd>
        </template>
      </i18n-t>
    </VSnackbar>
    <ol
      class="results-grid grid grid-cols-2 gap-4"
      :class="
        isSidebarVisible
          ? 'lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5'
          : 'sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6'
      "
      :aria-label="t('browsePage.aria.results', { query: searchTerm })"
    >
      <template v-for="item in results">
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
          :is-related="false"
        />
      </template>
    </ol>
  </div>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed } from "vue"
import { storeToRefs } from "pinia"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import { AudioDetail, ImageDetail, isDetail } from "~/types/media"

import type { SupportedMediaType } from "~/constants/media"

import VSnackbar from "~/components/VSnackbar.vue"
import VImageCell from "~/components/VImageCell/VImageCell.vue"
import VAudioResult from "~/components/VSearchResultsGrid/VAudioResult.vue"
import VContentLink from "~/components/VContentLink/VContentLink.vue"

defineProps<{
  results: (AudioDetail | ImageDetail)[]
  searchTerm: string
}>()

const {
  $i18n: { t },
} = useNuxtApp()
const mediaStore = useMediaStore()
const searchStore = useSearchStore()

const contentLinkPath = (mediaType: SupportedMediaType) =>
  searchStore.getSearchPath({ type: mediaType })

const resultCounts = computed(() => mediaStore.resultCountsPerMediaType)

const uiStore = useUiStore()
const {
  areInstructionsVisible: isSnackbarVisible,
  isFilterVisible: isSidebarVisible,
} = storeToRefs(uiStore)

const isSm = computed(() => uiStore.isBreakpoint("sm"))
</script>
