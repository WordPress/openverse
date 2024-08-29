<script setup lang="ts">
import { computed } from "vue"
import { storeToRefs } from "pinia"

import { useUiStore } from "~/stores/ui"

import { type AudioDetail, type ImageDetail, isDetail } from "~/types/media"

import VImageCell from "~/components/VImageCell/VImageCell.vue"
import VAudioResult from "~/components/VSearchResultsGrid/VAudioResult.vue"
import VAudioInstructions from "~/components/VSearchResultsGrid/VAudioInstructions.vue"

defineProps<{
  searchTerm: string
  results: (AudioDetail | ImageDetail)[]
  collectionLabel: string
}>()

const uiStore = useUiStore()
const { isFilterVisible: isSidebarVisible } = storeToRefs(uiStore)

const isSm = computed(() => uiStore.isBreakpoint("sm"))
</script>

<template>
  <div>
    <VAudioInstructions kind="all" />
    <ol
      class="grid grid-cols-2 gap-4"
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
          kind="search"
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
