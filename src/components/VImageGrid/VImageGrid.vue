<template>
  <section>
    <div class="image-grid flex flex-wrap gap-4">
      <VImageCell
        v-for="(image, index) in images"
        :key="index"
        :image="image"
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

<script>
/**
 * This component receives an array of images as a prop, and
 * is responsible for displaying them as a grid.
 * It can also fetch more images when 'Load More' clicked,
 * or display 'No More Media'.
 * Used to display both image search results, and related images.
 */
import VLoadMore from '~/components/VLoadMore.vue'
import VImageCell from '~/components/VImageGrid/VImageCell.vue'

export default {
  name: 'ImageGrid',
  components: { VLoadMore, VImageCell },
  props: {
    images: {
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
      required: true,
    },
  },

  computed: {
    isError() {
      return !!this.fetchState.fetchingError
    },
  },
  methods: {
    onLoadMore() {
      this.$emit('load-more')
    },
  },
}
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
