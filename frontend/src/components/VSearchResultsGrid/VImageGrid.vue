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

<script lang="ts">
/**
 * This component receives an array of images as a prop, and
 * is responsible for displaying them as a grid.
 * It can also fetch more images when 'Load More' is clicked.
 * Used to display both image search results, and related images.
 */
import { computed, defineComponent, PropType } from "vue"

import { useSearchStore } from "~/stores/search"

import type { ImageDetail } from "~/types/media"
import type { ResultKind } from "~/types/result"

import VImageCell from "~/components/VImageCell/VImageCell.vue"

export default defineComponent({
  name: "ImageGrid",
  components: { VImageCell },
  props: {
    results: {
      type: Array as PropType<ImageDetail[]>,
      default: () => [],
    },
    /**
     * `VImageGrid` is used for the image search results, related images,
     * and the image collection page.
     * The load more button is not shown for related images.
     */
    kind: {
      type: String as PropType<ResultKind>,
      default: "search",
    },
    imageGridLabel: {
      type: String,
      required: true,
    },
    relatedTo: {
      type: String,
      default: "null",
    },
  },
  setup() {
    const searchStore = useSearchStore()

    const searchTerm = computed(() => searchStore.searchTerm)

    return { searchTerm }
  },
})
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
