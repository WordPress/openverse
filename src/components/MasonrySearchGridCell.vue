<template>
  <div>
    <figure class="search-grid_item">
      <a
        :href="'photos/' + image.id"
        @click="onGotoDetailPage($event, image)"
        class="search-grid_image-ctr">
        <img
          :class="{'search-grid_image': true, 'search-grid_image__fill': !shouldContainImage}"
          :alt="image.title" :src="getImageUrl(image)"
          @error="onImageLoadError">
      </a>
      <figcaption class="search-grid_item-overlay search-grid_item-overlay__top">
        <license-icons :image="image"></license-icons>
      </figcaption>
      <figcaption class="search-grid_item-overlay search-grid_item-overlay__bottom">
        <a class="search-grid_overlay-provider"
            :title="image.title"
            :href="getImageForeignUrl(image)"
            @click.stop="() => false"
            target="new">
            <img class="search-grid_overlay-provider-logo" :alt="image.provider"
                :src="getProviderLogo(image.provider)">
            {{ image.title }}
        </a>
      </figcaption>
    </figure>
  </div>
</template>

<script>
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
  name: 'masonry-search-grid-cell',
  props: ['image', 'includeAddToList', 'shouldContainImage'],
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
      const logoUrl = require(`@/assets/${logo}`); // eslint-disable-line global-require, import/no-dynamic-require

      return logoUrl;
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
    onImageLoadError(event) {
      const image = event.target;
      image.src = errorImage;
    },
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .search-grid_image-ctr {
    background: #EBECE4;
    display: block;
    width: 100%;
  }

  .search-grid_item {
    overflow: hidden;

    &:hover .search-grid_item-overlay {
      opacity: 1;
      bottom: 0;
    }

    &:hover .search-grid_item-overlay__top {
      top: 0;
    }
  }

  .search-grid_item-overlay {
    position: absolute;
    opacity: 0;
    transition: all .4s ease;
    width: 100%;
    height: 30px;
    color: #fff;
    padding: 0 10px;
    display: block;
    top: -100%;

    &__top {
      transition: all .5s ease;
      background: linear-gradient(to bottom,
                  rgba(0,0,0,.5)
                  0,
                  rgba(0,0,0,0) 100%);
      top: 0;
    }

    &__bottom {
      height: 30px;
      background: linear-gradient(to top,
                  rgba(0,0,0,.5)
                  0,
                  rgba(0,0,0,0) 100%);
      bottom: -100%;
      top: auto;
    }
  }

  .search-grid_overlay-provider {
    width: calc( 100% - 30px );
    display: block;
    bottom: 10px;
    left: 10px;
    z-index: 100;
    color: #fff;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;

    &:hover {
      text-decoration: underline;
    }
  }

  .search-grid_overlay-provider-logo {
    max-height: 30px;
    max-width: 40px;
    margin-right: 5px;
    padding-bottom: 3px;
  }

  .search-grid_item {
    width: 100%;
    position: relative;
    display: block;
    float: left;
    flex: 0 0 auto;
    flex-grow: 1;
    cursor: pointer;
  }

  .search-grid_image {
    margin: auto;
    display: block;
  }

  .search-grid_image__fill {
    width: 100%;
  }

  @media screen and (max-width: 600px) {
    .search-grid_item-overlay {
      position: absolute;
      opacity: 1;
      bottom: 0;
    }

    .search-grid_overlay-add {
      position: absolute;
      width:  44px;
      height: 44px;
      bottom: 0;
    }

     .search-grid_layout-control {
      text-align: left !important;
    }
  }
</style>
