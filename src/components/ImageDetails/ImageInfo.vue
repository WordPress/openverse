<template>
  <section class="sidebar_section">
    <div class="mb-6">
      <dl>
        <dt class="mb-2">
          {{ $t('photo-details.information.type') }}
        </dt>
        <dd>{{ prettyImageType }}</dd>
        <dt class="mb-2">
          {{ $t('photo-details.information.dimensions') }}
        </dt>
        <dd>
          <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
          {{ imageWidth }} &times; {{ imageHeight }}
          <!-- eslint-enable -->
          {{ $t('photo-details.information.pixels') }}
        </dd>
        <dt v-if="providerName != sourceName" class="mb-2">
          {{ $t('photo-details.information.provider') }}
        </dt>
        <dd v-if="providerName != sourceName">
          {{ providerName }}
        </dd>
        <dt class="mb-2">
          {{ $t('photo-details.information.source') }}
        </dt>
        <dd>
          <a
            :aria-label="sourceName"
            :href="image.foreign_landing_url"
            target="blank"
            rel="noopener noreferrer"
            @click="onPhotoSourceLinkClicked"
            @keyup.enter="onPhotoSourceLinkClicked"
          >
            {{ sourceName }}
          </a>
        </dd>
      </dl>
    </div>
    <div class="mb-6">
      <h5 class="mb-2 b-header">
        {{ $t('photo-details.information.tags') }}
      </h5>
      <PhotoTags :tags="image.tags" :show-header="false" />
    </div>
  </section>
</template>

<script>
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/store-modules/usage-data-analytics-types'
import PhotoTags from '~/components/PhotoTags'
import getProviderName from '~/utils/getProviderName'
import getProviderLogo from '~/utils/getProviderLogo'

export default {
  name: 'ImageInfo',
  components: {
    PhotoTags,
  },
  props: [
    'image',
    'ccLicenseURL',
    'fullLicenseName',
    'imageWidth',
    'imageHeight',
    'imageType',
  ],
  computed: {
    providerName() {
      return getProviderName(
        this.$store.state.imageProviders,
        this.$props.image.provider
      )
    },
    prettyImageType() {
      if (this.imageType && this.imageType.split('/').length > 1) {
        return this.imageType.split('/')[1].toUpperCase()
      }
      return 'Unknown'
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
    onPhotoSourceLinkClicked() {
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType: DETAIL_PAGE_EVENTS.SOURCE_CLICKED,
        resultUuid: this.$props.image.id,
      })
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
  width: 92px;
  margin-right: 24px;
  display: inline-block;
}

dd {
  width: calc(100% - 92px - 28px);
}
</style>
