<template>
  <section class="sidebar_section">
    <div class="margin-bottom-big">
      <dl>
        <dt class="margin-bottom-small">Dimensions</dt>
        <dd>{{ imageWidth }} &times; {{ imageHeight }} pixels</dd>
        <dt class="margin-bottom-small">Provider</dt>
        <dd>{{ providerName }}</dd>
        <dt class="margin-bottom-small">Source</dt>
        <dd>
          <a
            :href="image.foreign_landing_url"
            target="blank"
            rel="noopener noreferrer"
          >
            {{ sourceName }}
          </a>
        </dd>
      </dl>
    </div>
    <div class="margin-bottom-big">
      <h5 class="is-block margin-bottom-small b-header">License</h5>
      <license-icons :license="image.license"></license-icons>
      <a class="photo_license body-big" :href="ccLicenseURL">
        {{ fullLicenseName }}
      </a>
    </div>
    <div class="margin-bottom-big">
      <h5 class="is-block margin-bottom-small b-header">Tags</h5>
      <photo-tags :tags="image.tags" :showHeader="false" />
    </div>
  </section>
</template>

<script>
import PhotoTags from '@/components/PhotoTags'
import getProviderName from '@/utils/getProviderName'
import LicenseIcons from '@/components/LicenseIcons'
import getProviderLogo from '@/utils/getProviderLogo'

export default {
  name: 'image-info',
  props: [
    'image',
    'ccLicenseURL',
    'fullLicenseName',
    'imageWidth',
    'imageHeight',
  ],
  components: {
    LicenseIcons,
    PhotoTags,
  },
  computed: {
    providerName() {
      return getProviderName(
        this.$store.state.imageProviders,
        this.$props.image.provider
      )
    },
    sourceName() {
      return getProviderName(
        this.$store.state.imageProviders,
        this.$props.image.source
      )
    },
  },
  methods: {
    getProviderLogo(providerName) {
      return getProviderLogo(providerName)
    },
  },
}
</script>

<style lang="scss" scoped>
.report {
  font-size: 0.8rem !important;
  text-transform: none !important;

  &:hover {
    background: none !important;
  }

  &:focus {
    background: none !important;
  }
}

dl {
  display: flex;
  flex-wrap: wrap;
}

dt {
  font-weight: bold;
  width: 90px;
  margin-right: 24px;

  &:after {
    content: ':';
  }
}

dd {
  width: calc(100% - 90px - 24px);
}
</style>
