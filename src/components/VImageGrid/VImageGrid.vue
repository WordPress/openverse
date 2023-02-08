<template>
  <section>
    <div class="image-grid flex flex-wrap gap-4">
      <VImageCell
        v-for="(image, index) in images"
        :key="image.id"
        :image="image"
        :search-term="searchTerm"
        @shift-tab="handleShiftTab($event, index)"
      />
    </div>
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
import { computed, defineComponent, PropType } from "@nuxtjs/composition-api"

import { useSearchStore } from "~/stores/search"

import type { FetchState } from "~/types/fetch-state"
import type { ImageDetail } from "~/types/media"

import { defineEvent } from "~/types/emits"

import VLoadMore from "~/components/VLoadMore.vue"
import VImageCell from "~/components/VImageGrid/VImageCell.vue"

export default defineComponent({
  name: "ImageGrid",
  components: { VLoadMore, VImageCell },
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
      type: Object as PropType<FetchState>,
      required: true,
    },
  },
  emits: {
    "shift-tab": defineEvent(),
  },
  setup(props, { emit }) {
    const searchStore = useSearchStore()

    const searchTerm = computed(() => searchStore.searchTerm)
    const isError = computed(() => Boolean(props.fetchState.fetchingError))

    const handleShiftTab = (event: KeyboardEvent, index: number) => {
      if (index === 0) {
        event.preventDefault()
        emit("shift-tab")
      }
    }

    return { isError, handleShiftTab, searchTerm }
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
