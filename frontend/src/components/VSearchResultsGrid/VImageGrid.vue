<template>
  <section>
    <VGridSkeleton
      v-if="!images.length && !fetchState.isFinished"
      is-for-tab="image"
    />
    <ol class="image-grid flex flex-wrap gap-4" :aria-label="imageGridLabel">
      <VImageCell
        v-for="image in images"
        :key="image.id"
        :image="image"
        :search-term="searchTerm"
        aspect-ratio="intrinsic"
        :related-to="relatedTo"
      />
    </ol>
    <h5 v-if="isError && !fetchState.isFinished" class="py-4">
      {{ fetchState.fetchingError }}
    </h5>
    <footer v-if="!isSinglePage" class="pt-4">
      <VLoadMore />
    </footer>
  </section>
</template>

<script lang="ts">
/**
 * This component receives an array of images as a prop, and
 * is responsible for displaying them as a grid.
 * It can also fetch more images when 'Load More' clicked,
 * or display 'No More Media'.
 * Used to display both image search results, and related images.
 */
import { computed, defineComponent, PropType } from "vue"

import { useSearchStore } from "~/stores/search"
import { useRelatedMediaStore } from "~/stores/media/related-media"

import type { FetchState } from "~/types/fetch-state"
import type { ImageDetail } from "~/types/media"

import VGridSkeleton from "~/components/VSkeleton/VGridSkeleton.vue"
import VLoadMore from "~/components/VLoadMore.vue"
import VImageCell from "~/components/VSearchResultsGrid/VImageCell.vue"

import type { NuxtError } from "@nuxt/types"

export default defineComponent({
  name: "ImageGrid",
  components: { VGridSkeleton, VLoadMore, VImageCell },
  props: {
    images: {
      type: Array as PropType<ImageDetail[]>,
      default: () => [],
    },
    /**
     * VImageGrid is used for the search grid and the related images.
     * In the related images, it is just a single page of results without the
     * "Load More" button, and in the search grid it is a grid that can load
     * more images on the "Load More" button click.
     */
    isSinglePage: {
      type: Boolean,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState<NuxtError>>,
      required: true,
    },
    imageGridLabel: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const searchStore = useSearchStore()

    const searchTerm = computed(() => searchStore.searchTerm)
    const isError = computed(() => props.fetchState.fetchingError !== null)

    const relatedTo = computed(() => {
      return props.isSinglePage ? useRelatedMediaStore().mainMediaId : null
    })

    return { isError, searchTerm, relatedTo }
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
