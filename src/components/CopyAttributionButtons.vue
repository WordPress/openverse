<template>
  <section class="sidebar_section">
    <header class="sidebar_section-header">
      <h2>
        Image Attribution
      </h2>
    </header>
    <image-attribution :image="image"
                       :ccLicenseURL="image.license_url"
                       :fullLicenseName="fullLicenseName" />
    <div class="attribution-buttons">
      <CopyButton :toCopy="HTMLAttribution"
                  contentType="html"
                  title="Can be used in website code">
        HTML code
      </CopyButton>
      <CopyButton :toCopy="textAttribution"
                  contentType="text"
                  title="Can be used in static documents">
        Plain text
      </CopyButton>
      <CopyButton :toCopy="HTMLAttribution"
                  contentType="rtf"
                  title="Can be used in WYSIWYG editors">
        Rich text
      </CopyButton>
    </div>
  </section>
</template>

<script>
import CopyButton from '@/components/CopyButton';
import ImageAttribution from '@/components/ImageAttribution';

export default {
  name: 'copy-attribution-buttons',
  props: ['image', 'ccLicenseURL', 'fullLicenseName'],
  components: {
    CopyButton,
    ImageAttribution,
  },
  computed: {
    textAttribution() {
      return () => {
        const image = this.image;
        const licenseURL = this.ccLicenseURL;
        const byCreator = image.creator ? `by ${image.creator}` : ' ';

        return `"${image.title}" ${byCreator}
                is licensed under ${this.fullLicenseName.toUpperCase()}. To view a copy of this license, visit: ${licenseURL}`;
      };
    },
    HTMLAttribution() {
      return () => {
        const image = this.image;

        let byCreator;
        if (image.creator) {
          if (image.creator_url) {
            byCreator = `by <a href="${image.creator_url}">${image.creator}</a>`;
          }
          else {
            byCreator = `by ${image.creator}`;
          }
        }
        else {
          byCreator = ' ';
        }

        return `<a href="${image.foreign_landing_url}">"${image.title}"</a>
                ${byCreator}
                is licensed under
                <a href="${this.ccLicenseURL}">
                  ${this.fullLicenseName.toUpperCase()}
                </a>`;
      };
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
