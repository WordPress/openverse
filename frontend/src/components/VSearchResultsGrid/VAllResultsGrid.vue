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
    <VAudioInstructions kind="all" />
    <ol
      class="results-grid grid grid-cols-2 gap-4"
      :class="
        isSidebarVisible
          ? 'lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5'
          : 'sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6'
      "
      :aria-label="collectionLabel"
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
          kind="search"
        />
      </template>
    </ol>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, type PropType } from "vue"
import { storeToRefs } from "pinia"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import { type AudioDetail, type ImageDetail, isDetail } from "~/types/media"

import type { SupportedMediaType } from "~/constants/media"

import VImageCell from "~/components/VImageCell/VImageCell.vue"
import VAudioResult from "~/components/VSearchResultsGrid/VAudioResult.vue"
import VContentLink from "~/components/VContentLink/VContentLink.vue"
import VAudioInstructions from "~/components/VSearchResultsGrid/VAudioInstructions.vue"

export default defineComponent({
  name: "VAllResultsGrid",
  components: {
    VImageCell,
    VAudioResult,
    VAudioInstructions,
    VContentLink,
  },
  props: {
    searchTerm: {
      type: String,
      required: true,
    },
    results: {
      type: Array as PropType<(AudioDetail | ImageDetail)[]>,
      required: true,
    },
    collectionLabel: {
      type: String,
      required: true,
    },
  },
  setup() {
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

    return {
      resultCounts,

      contentLinkPath,

      isSidebarVisible,
      isSnackbarVisible,
      isSm,

      isDetail,
    }
  },
})
</script>
