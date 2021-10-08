<template>
  <section class="image-grid">
    <div class="image-grid__cells">
      <ImageCell v-for="(image, index) in images" :key="index" :image="image" />
    </div>
    <h5 v-if="isError" class="image-grid__notification py-4">
      {{ errorMessageText }}
    </h5>
    <LoadMoreButton
      v-if="canLoadMore"
      :is-error="isError"
      :is-fetching="isFetching"
      :is-finished="isFinished"
      data-testid="load-more"
      @onLoadMore="onLoadMoreImages"
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
    isFetching: {
      type: Boolean,
      default: false,
    },
    fetchingError: {
      default: null,
    },
    errorMessageText: {
      type: String,
      default: '',
    },
    isFinished: {
      type: Boolean,
      default: false,
    },
  },

  computed: {
    isError() {
      return !!this.fetchingError
    },
    fetchingErrorHeading() {
      const type = this.$t('browse-page.search-form.image')
      return this.$t('browse-page.fetching-error', { type })
    },
  },
  methods: {
    onLoadMoreImages() {
      this.$emit('onLoadMoreImages')
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
    margin: 10px;

    @include tablet {
      &:after {
        content: '';
        flex-grow: 999999999;
      }
    }
  }
}
</style>
