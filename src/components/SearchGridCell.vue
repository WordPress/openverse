<template>
  <figure class="search-grid_item">
        <a :href="'photos/' + image.id"
          @click="onGotoDetailPage($event, image)"
          class="search-grid_image-ctr">
          <img class="search-grid_image" :alt="image.title" :src="getImageUrl(image)"
               @error="onImageLoadError">
        </a>
        <figcaption class="search-grid_item-overlay search-grid_item-overlay__top">
          <license-icons :image="image"></license-icons>
        </figcaption>
        <figcaption class="search-grid_item-overlay search-grid_item-overlay__bottom">
          <a class="search-grid_overlay-provider"
             :href="getImageForeignUrl(image)"
             @click.stop="() => false"
             target="new">
             <img class="search-grid_overlay-provider-logo" :alt="image.provider"
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
import { SELECT_IMAGE_FOR_LIST } from '@/store/mutation-types';
import ImageProviderService from '@/api/ImageProviderService';
import LicenseIcons from '@/components/LicenseIcons';

const errorImage = require('@/assets/404-grid_placeholder.png');

const toAbsolutePath = (url, prefix = 'https://') => {
  if (url.indexOf('http://') >= 0 || url.indexOf('https://') >= 0) {
    return url;
  }
  return `${prefix}${url}`;
};

export default {
  name: 'search-grid-cell',
  props: ['image', 'includeAddToList'],
  components: {
    LicenseIcons,
  },
  methods: {
    getImageUrl(image) {
      if (!image) {
        return '';
      }

      const url = image.thumbnail || image.url;

      return toAbsolutePath(url);
    },
    getImageForeignUrl(image) {
      return toAbsolutePath(image.foreign_landing_url);
    },
    getProviderLogo(providerName) {
      const logo = ImageProviderService.getProviderInfo(providerName).logo;
      const logUrl = require(`@/assets/${logo}`); // eslint-disable-line global-require, import/no-dynamic-require

      return logUrl;
    },
    onGotoDetailPage(event, image) {
      // doesn't use router to redirect to photo details page in case the user
      // has the Command (Mac) or Ctrl Key (Windows) pressed, so that they can
      // open the page on a new tab with either of those keys pressed.
      if (!event.metaKey && !event.ctrlKey) {
        event.preventDefault();
        this.$router.push(`/photos/${image.id}`);
      }
    },
    onAddToImageList(image, event) {
      const imageWithDimensions = image || {};
      imageWithDimensions.pageX = event.pageX;
      imageWithDimensions.pageY = event.pageY;

      this.$store.commit(SELECT_IMAGE_FOR_LIST, { image: imageWithDimensions });
    },
    onImageLoadError(event) {
      const image = event.target;
      image.src = errorImage;
    },
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped></style>
