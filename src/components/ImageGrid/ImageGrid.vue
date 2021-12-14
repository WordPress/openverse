<template>
  <section class="image-grid my-6">
    <div class="image-grid__cells">
      <ImageCell v-for="(image, index) in images" :key="index" :image="image" />
    </div>
    <h5 v-if="isError" class="image-grid__notification py-4">
      {{ fetchState.fetchingError }}
    </h5>
    <LoadMoreButton
      v-if="canLoadMore"
      :is-error="isError"
      :is-fetching="fetchState.isFetching"
      :is-finished="fetchState.isFinished"
      data-testid="load-more"
      @onLoadMore="onLoadMore"
    />
  </section>
</template>

<script>
/**
 * This component receives an array of images as prop, and
 * is responsible for displaying them as a grid.
 * It can also fetch more images when 'Load More' clicked,
 * or display 'No More Media'.
 * Used to display both image search results, and related images.
 */
import LoadMoreButton from '~/components/ImageGrid/LoadMoreButton'
import ImageCell from '~/components/ImageGrid/ImageCell'

export default {
  name: 'ImageGrid',
  components: { LoadMoreButton, ImageCell },
  props: {
    images: {
      default: () => [],
    },
    canLoadMore: {
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
    fetchingErrorHeading() {
      const type = this.$t('browse-page.search-form.image')
      return this.$t('browse-page.fetching-error', { type })
    },
  },
  methods: {
    onLoadMore() {
      this.$emit('load-more')
    },
  },
}
</script>

<style lang="scss" scoped>
.image-grid {
  &__notification {
    display: flex;
    justify-content: center;
  }
  &__cells {
    display: flex;
    flex-wrap: wrap;

    @include tablet {
      &:after {
        content: '';
        flex-grow: 999999999;
      }
    }
  }
}
</style>
