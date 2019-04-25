<template>
  <section class="sidebar_section">
    <header class="sidebar_section-header">
      <h2>
        Image Attribution
      </h2>
    </header>
    <image-attribution id= "attribution"
                       :image="image"
                       :ccLicenseURL="image.license_url"
                       :fullLicenseName="fullLicenseName" />
    <span class='copy-description'>
        Copy the attribution text above. You can then paste it into your blog or document
      </span>
    <div class="button-group">
      <CopyButton :toCopy="HTMLAttribution"
                  contentType="rtf"
                  title="Can be used in WYSIWYG editors">
        Copy Attribution
      </CopyButton>
      <a class="dropdown button arrow-only" @click.prevent="toggleMoreOptions">
        <span class="show-for-sr">More copy options</span>
      </a>
      <help-tooltip
            tooltip="Copy the attribution text in rich text format so you can
                     use it in word processing software or a rich text editor" />
    </div>

    <div v-if="showMore" class="more-options">
      <div>
        <CopyButton :toCopy="textAttribution"
                    contentType="text"
                    title="Can be used in static documents">
          Plain text
        </CopyButton>
        <help-tooltip
          tooltip="Copy the attribution text in plain text format so
                    you can add it to any digital or printed document" />
      </div>
    </div>
  </section>
</template>

<script>
import CopyButton from '@/components/CopyButton';
import ImageAttribution from '@/components/ImageAttribution';
import HelpTooltip from '@/components/HelpTooltip';

export default {
  name: 'copy-attribution-buttons',
  props: ['image', 'ccLicenseURL', 'fullLicenseName'],
  components: {
    CopyButton,
    ImageAttribution,
    HelpTooltip,
  },
  data() {
    return {
      showMore: false,
    };
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
    moreOptionsText() {
      return this.showMore ? 'Less ▲' : 'More ▼';
    },
  },
  methods: {
    toggleMoreOptions() {
      this.showMore = !this.showMore;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';


</style>
