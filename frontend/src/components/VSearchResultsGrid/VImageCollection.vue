<template>
  <section>
    <ol class="image-grid flex flex-wrap gap-4" :aria-label="collectionLabel">
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
 */
import { defineComponent, type PropType } from "vue"

import type { ResultKind } from "~/types/result"
import type { ImageDetail } from "~/types/media"

import VImageCell from "~/components/VImageCell/VImageCell.vue"

export default defineComponent({
  name: "VImageCollection",
  components: { VImageCell },
  props: {
    results: {
      type: Array as PropType<ImageDetail[]>,
      required: true,
    },
    /**
     * `VImageGrid` is used for the image search results, related images,
     * and the image collection page.
     */
    kind: {
      type: String as PropType<ResultKind>,
      default: "search",
    },
    collectionLabel: {
      type: String,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
    relatedTo: {
      type: String as PropType<string | null>,
      default: null,
    },
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
