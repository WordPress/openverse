<template>
    <div class="photo grid-x">
      <div class="photo_image-ctr cell medium-12 large-8">
        <a class="photo_breadcrumb"
           :href="breadCrumbURL"
           @click.prevent="onGoBackToSearchResults"
           v-if="shouldShowBreadcrumb">&#171; Back to search results</a>
        <img @load="onImageLoad"
             :class="photo_image"
             :src="image.url"
             :alt="image.title">
      </div>
      <div class="photo_info-ctr cell medium-12 large-4">
        <header class="photo_info-header">
          <h2>
            PHOTO INFO
          </h2>
        </header>
        <ul>
          <li>
            <h3>Title</h3>
            <span>{{ image.title }}</span>
          </li>
          <li>
            <h3>Creator</h3>
            <span>
            <a :href="image.creator_url">{{ image.creator }}</a>
            </span>
          </li>
          <li>
            <h3>License</h3>
            <a class="photo_license" :href="ccLicenseURL">
            CC {{ image.license }} {{ image.license_version }}
            </a>
            <license-icons :image="image"></license-icons>
          </li>
          <li>
            <h3>Source</h3>
            <a class="photo_provider"
               :href="image.foreign_landing_url"
               target="blank"
               rel="noopener noreferrer">{{ image.provider }}</a>
          </li>
          <li>
            <h3>Dimensions</h3>
            <span> {{ imageWidth }} <span> X </span> {{ imageHeight }} pixels</span>
          </li>
        </ul>
        <section class="photo_usage">
          <header class="photo_info-header">
            <h2>
              Photo Attribution
            </h2>
          </header>
          <p class="photo_usage-attribution" ref="photoAttribution">
            <a :href="image.foreign_landing_url">"{{ image.title }}"</a>
            by
            <a :href="image.creator_url">{{ image.creator }}</a>
            is licensed under
            <a class="photo_license" :href="ccLicenseURL">
            CC {{ image.license}} {{ image.license_version }}
            </a>
          </p>
          <CopyButton :toCopy="HTMLAttribution">Copy to HTML</CopyButton>
          <CopyButton :toCopy="textAttribution">Copy to Text</CopyButton>
        </section>
      </div>
    </div>
</template>

<script>
import CopyButton from '@/components/CopyButton';

export default {
  name: 'photo-details',
  props: ['image', 'breadCrumbURL', 'shouldShowBreadcrumb', 'query', 'imageWidth', 'imageHeight'],
  components: {
    CopyButton,
  },
  computed: {
    ccLicenseURL() {
      if (!this.image) {
        return '';
      }

      const image = this.image;
      const BASE_URL = 'https://creativecommons.org';
      let url = `${BASE_URL}/licenses/${image.license}/${image.license_version}`;
      let license = '';

      if (image.license) {
        license = image.license;
      }

      if (license === 'cc0') {
        url = `${BASE_URL}/publicdomain/zero/1.0/`;
      } else if (image.license === 'pdm') {
        url = `${BASE_URL}/publicdomain/mark/1.0/`;
      }

      return url;
    },
    textAttribution() {
      const image = this.image;
      const licenseURL =
        `<a href="${this.ccLicenseURL}">
          CC ${image.license.toUpperCase()} ${image.license_version}
         </a>`;

      return `"${image.title}" by ${image.creator}
              is licensed under CC ${image.license.toUpperCase()}
              ${image.license_version} ${licenseURL}`;
    },
    HTMLAttribution() {
      const image = this.image;

      return `<a href="${image.foreign_landing_url}">"${image.title}"</a>
              by
              <a href="${image.creator_url}">${image.creator}</a>
              is licensed under
              <a href="${this.ccLicenseURL}">
                CC ${image.license.toUpperCase()} ${image.license_version}
              </a>`;
    },
  },
  methods: {
    onGoBackToSearchResults() {
      this.$router.push({ name: 'browse-page', query: { q: this.query } });
    },
    onImageLoad(event) {
      this.$emit('onImageLoaded', event);
    },
  },
};
</script>

<style lang="scss" scoped>
  .photo_provider {
     text-transform: capitalize;
  }

  .photo {
    width: 100%;
    border-bottom: 1px solid #d6d6d6;
  }

  .photo_breadcrumb {
    width: 100%;
    display: block;
    text-align: left;
    font-size:.9em;
    margin-top: -10px;
  }

  .photo_image-ctr {
    position: relative;
    text-align: center;
    padding: 30px;
    max-height: 640px;

    img {
      position: relative;
      width: auto;
      height: auto;
      max-height: 100%;
      max-width: 100%;
      background: #EBECE4;
    }

    /* Small only */
    @media screen and (max-width: 39.9375em) {
      padding: 30px 15px;
    }
  }

  .photo_info-ctr {
    padding: 45px 15px;
    border-left: 1px solid #d6d6d6;

    .photo_info-header {
      border-top: 1px solid #e7e8e9;
      margin-left: 15px;
    }

    h4 {
      font-size: 1.25rem;
      font-weight: 500;
      line-height: 1rem;
      margin: 0;
      padding: 0 0 0 15px;
    }

    h3 {
      font-size: 1rem;
      font-weight: 500;
      line-height: 1rem;
      margin: 0;
    }

    h2 {
      margin-bottom: 1.07142857em;
      font-size: .875em;
      font-weight: 600;
      letter-spacing: 1px;
      line-height: 1.25;
      text-transform: uppercase;
      display: inline-block;
      padding-top: .28571429em;
      border-top: 5px solid rgba(29, 31, 39, .8);
      margin-top: -3px;
    }

    ul {
      margin: 0;
      list-style-type: none;

      li {
        padding-left: 15px;
        margin-left: 0;
        margin-bottom: 10px;
      }
    }

    /* Small only */
    @media screen and (max-width: 39.9375em) {
      padding: 30px 0;
    }
  }

  .photo_usage {
    .photo_info-header {
      margin-left: 0px;
    }

    padding: 15px;
  }

  .photo_usage-attribution {
    border-left: 1px solid #e7e8e9;;
    padding-left: 10px;
    padding-bottom: 15px
  }
</style>

