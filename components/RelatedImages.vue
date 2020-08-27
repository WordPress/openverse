<template>
  <div
    class="photo_related-images"
    v-if="relatedImages && relatedImages.length > 0"
  >
    <h3 class="b-header">{{ $t('photo-details.related-images') }}</h3>
    <search-grid
      :imagesCount="imagesCount"
      :images="relatedImages"
      :query="query"
      :filter="filter"
      :includeAnalytics="false"
      :useInfiniteScroll="false"
      :includeAddToList="false"
      v-if="isPrimaryImageLoaded === true"
    >
    </search-grid>
  </div>
</template>

<script>
export default {
  name: 'related-images',
  props: [
    'relatedImages',
    'imagesCount',
    'query',
    'filter',
    'isPrimaryImageLoaded',
  ],
}
</script>

<style lang="scss">
@import '../src/styles/photodetails.scss';

.photo_related-images .search-grid-cells {
  margin: 10px -10px;
}
</style>
