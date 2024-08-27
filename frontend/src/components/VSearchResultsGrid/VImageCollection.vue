<script setup lang="ts">
/**
 * This component receives an array of images as a prop, and
 * is responsible for displaying them as a grid.
 */

import type { CollectionComponentProps } from "~/types/collection-component-props"

import VImageCell from "~/components/VImageCell/VImageCell.vue"

withDefaults(defineProps<CollectionComponentProps<"image">>(), {
  relatedTo: "null",
})
</script>

<template>
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
</template>

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
