<template>
  <section class="pt-2 sm:pt-0">
    <ol class="image-grid flex flex-wrap gap-4" :aria-label="imageGridLabel">
      <VImageCell
        v-for="image in results"
        :key="image.id"
        :image="image"
        :search-term="searchTerm"
        aspect-ratio="intrinsic"
        :kind="kind"
        :related-to="relatedTo"
      />
    </ol>
  </section>
</template>

<script setup lang="ts">
/**
 * This component receives an array of images as a prop, and
 * is responsible for displaying them as a grid.
 * It can also fetch more images when 'Load More' is clicked.
 * Used to display both image search results, and related images.
 */
import { computed } from "vue"

import { useSearchStore } from "~/stores/search"

import type { ImageDetail } from "~/types/media"
import type { ResultKind } from "~/types/result"

import VImageCell from "~/components/VImageCell/VImageCell.vue"

withDefaults(
  defineProps<{
    results: ImageDetail[]
    kind: ResultKind
    imageGridLabel: string
    relatedTo?: string
  }>(),
  { relatedTo: "null" }
)
/**
 * `VImageGrid` is used for the image search results, related images,
 * and the image collection page.
 * The load more button is not shown for related images.
 */
const searchStore = useSearchStore()

const searchTerm = computed(() => searchStore.searchTerm)
</script>

<style scoped>
@screen md {
  .image-grid:after {
    /**
   * This keeps the last item in the results from expanding to fill
   * all available space, which can result in a final row with a
   * single, 100% wide image.
   */

    content: "";
    flex-grow: 999999999;
  }
}
</style>
