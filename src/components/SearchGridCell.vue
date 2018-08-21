<template>
  <figure v-for="(image, index) in images"
   	:class="search-grid_item"
    :key="index"
    @click="onGotoDetailPage(image)">
   	<a :href="image.foreign_landing_url"
         @click.prevent="() => false"
         target="new">
     	<img class="search-grid_image" :src="image.thumbnail || image.url">
  	</a>
	  <figcaption class="search-grid_item-overlay">
	    <a class="search-grid_overlay-title"
	       :href="image.foreign_landing_url"
	       @click.stop="() => false"
	       target="new">
	       {{ image.title }}
	    </a>
	    <a class="search-grid_overlay-add"
	       @click.stop="onAddToImageList(image)"
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
