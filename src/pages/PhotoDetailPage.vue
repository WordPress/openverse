<template>
  <div class="photo-detail-page">
    <div class="x-grid">
      <div class="cell">
        <header-section showNavSearch="true" fixedNav="true"></header-section>
      </div>
    </div>
    <div class="photo">
      <div class="photo_ctr">
        <div class="photo_image-ctr">
          <img :src="image.url" />
        </div>
        <div class="photo_info-ctr">
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
              <a :href="ccLicenseURL">
              CC {{ image.license}} {{ image.license_version }}
              </a>
            </li>
            <li>
              <h3>Source</h3>
              <a :href="image.foreign_landing_url">{{ image.provider }}</a>
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
              <a :href="ccLicenseURL">
              CC {{ image.license}} {{ image.license_version }}
              </a>
            </p>
            <button class="button photo_copy-btn
              photo_copy-btn__html"
              data-type="html">
            Copy to HTML</button>
            <button class="button
              photo_copy-btn
              photo_copy-btn__text"
              data-type="text">
            Copy to Text
            </button>
          </section>
        </div>
      </div>
    </div>
    <div class="photo_related-content">
      <h5>Related</h5>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import { FETCH_IMAGE } from '@/store/action-types';
import Clipboard from 'clipboard';


const PhotoDetailPage = {
  name: 'photo-detail-page',
  components: {
    HeaderSection,
    FooterSection,
  },
  computed: {
    image() {
      return this.$store.state.image;
    },
    ccLicenseURL() {
      const image = this.image;
      const url = 'https://creativecommons.org/licenses';

      return `${url}/${image.license}/${image.license_version}`;
    },
    textAttribution() {
      const image = this.image;

      return `"${image.title}" by ${image.creator}
              is licensed under CC ${image.license}
              ${image.license_version}`;
    },
    HTMLAttribution() {
      const image = this.image;

      return `<a href="${image.foreign_landing_url}">"${image.title}"</a>
              by
              <a href="${image.creator_url}">${image.creator}</a>
              is licensed under
              <a href="${this.ccLicenseURL}">
                CC ${image.license} ${image.license_version}
              </a>`;
    },
  },
  methods: {
    initClipboard() {
      new Clipboard('.photo_copy-btn', {
        text: element => {
          let attributionContent;
          if (element.getAttribute('data-type') === 'html') {
            attributionContent = this.HTMLAttribution;
          } else {
            attributionContent = this.textAttribution;
          }

          return attributionContent.replace(/\s\s/g, '');
        },
      });
    },
  },
  created() {
    this.id = this.$route.params.id;
    if (this.id) {
      this.$store.dispatch(FETCH_IMAGE, { id: this.id });
    }

    this.initClipboard();
  },
};

export default PhotoDetailPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .photo_ctr {
    display: flex;
    border-bottom: 1px solid #d6d6d6;
  }

  .photo_image-ctr {
    width: calc( 100% - 400px );
    text-align: center;
    margin: 45px;
    height: 100%;
    max-height: 640px;

    img {
      width: auto;
      max-height: 640px;
    }
  }

  .photo_info-ctr {
    padding: 45px 0;
    border-left: 1px solid #d6d6d6;
    width: 400px;

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

  .photo_copy-btn {
    border-radius: 3px;
    width: 49%;
  }

  .photo_copy-btn__html {
    background: #4A69CA;
  }

  .photo_copy-btn__text {
    background: #4A69CA;
  }
</style>
