<template>
  <section>
    <div class="image-grid flex flex-wrap gap-4">
      <VImageCell
        v-for="(image, index) in images"
        :key="index"
        :image="image"
        @shift-tab="handleShiftTab($event, index)"
      />
    </div>
    <h5 v-if="isError && !fetchState.isFinished" class="py-4">
      {{ fetchState.fetchingError }}
    </h5>
    <footer v-if="showLoadMore" class="pt-4">
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
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { FetchState } from '~/composables/use-fetch-state'
import type { ImageDetail } from '~/models/media'

import { defineEvent } from '~/types/emits'

import VLoadMore from '~/components/VLoadMore.vue'
import VImageCell from '~/components/VImageGrid/VImageCell.vue'

export default defineComponent({
  name: 'ImageGrid',
  components: { VLoadMore, VImageCell },
  props: {
    images: {
      type: Array as PropType<ImageDetail[]>,
      default: () => [],
    },
    /**
     * Whether to show the 'Load More' button.
     * Is false for related images
     */
    showLoadMore: {
      type: Boolean,
      default: true,
    },
    fetchState: {
      type: Object as PropType<FetchState>,
      required: true,
    },
  },
  emits: {
    'load-more': defineEvent(),
    'shift-tab': defineEvent(),
  },
  setup(props, { emit }) {
    const isError = computed(() => Boolean(props.fetchState.fetchingError))

    const onLoadMore = () => {
      emit('load-more')
    }

    const handleShiftTab = (event: KeyboardEvent, index: number) => {
      if (index === 0) {
        event.preventDefault()
        emit('shift-tab')
      }
    }

    return { isError, onLoadMore, handleShiftTab }
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

    content: '';
    flex-grow: 999999999;
  }
}
</style>
