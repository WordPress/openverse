<template>
  <div
    v-if="relatedImages && relatedImages.length > 0"
    class="photo_related-images"
  >
    <h3 class="b-header">
      {{ $t('photo-details.related-images') }}
    </h3>
    <SearchGrid
      v-if="isPrimaryImageLoaded === true"
      :images-count="imagesCount"
      :images="relatedImages"
      :query="query"
      :filter="filter"
      :include-analytics="false"
      :use-infinite-scroll="false"
      :include-add-to-list="false"
    />
  </div>
</template>

<script>
export default {
  name: 'RelatedImages',
  props: [
    'relatedImages',
    'imagesCount',
    'query',
    'filter',
    'isPrimaryImageLoaded',
  ],
}
</script>

<style lang="scss" scoped>
@import '~/styles/photodetails.scss';

.photo_related-images .search-grid-cells {
  margin: 10px -10px;
}
</style>
