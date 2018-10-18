<template>
  <figure class="search-grid_item"
         :key="image.id"
         @click="onGotoDetailPage(image)">
    <a :href="image.foreign_landing_url"
      @click.prevent="() => false"
      target="new"
      class="search-grid_image-ctr">
      <img class="search-grid_image" :src="getImageUrl(image)"
           @error="onImageLoadError">
    </a>
    <figcaption class="search-grid_item-overlay search-grid_item-overlay__top">
      <license-icons :image="image"></license-icons>
    </figcaption>
    <figcaption class="search-grid_item-overlay search-grid_item-overlay__bottom">
      <a class="search-grid_overlay-provider"
         :href="image.foreign_landing_url"
         @click.stop="() => false"
         target="new">
         <img class="search-grid_overlay-provider-logo"
              :src="getProviderLogo(image.provider)">
         {{ image.title }}
      </a>
      <a class="search-grid_overlay-add"
         @click.stop="onAddToImageList(image, $event)"
         v-if="includeAddToList">
      </a>
    </figcaption>
  </figure>
</template>

<script>
export default {
  name: 'search-grid-cell',
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped></style>
