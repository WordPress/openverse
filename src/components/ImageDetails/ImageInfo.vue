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
} from '~/constants/usage-data-analytics-types'
import PhotoTags from '~/components/PhotoTags'
import getProviderName from '~/utils/get-provider-name'
import { PROVIDER, USAGE_DATA } from '~/constants/store-modules'
import { mapActions, mapState } from 'vuex'

export default {
  name: 'ImageInfo',
  components: {
    PhotoTags,
  },
  props: [
    'image',
    'licenseUrl',
    'fullLicenseName',
    'imageWidth',
    'imageHeight',
    'imageType',
  ],
  computed: {
    ...mapState(PROVIDER, ['imageProviders']),
    providerName() {
      return getProviderName(this.imageProviders, this.$props.image.provider)
    },
    prettyImageType() {
      if (this.imageType && this.imageType.split('/').length > 1) {
        return this.imageType.split('/')[1].toUpperCase()
      }
      return 'Unknown'
    },
    sourceName() {
      return getProviderName(this.imageProviders, this.$props.image.source)
    },
  },
  methods: {
    ...mapActions(USAGE_DATA, { sendEvent: SEND_DETAIL_PAGE_EVENT }),
    onPhotoSourceLinkClicked() {
      this.sendEvent({
        eventType: DETAIL_PAGE_EVENTS.SOURCE_CLICKED,
        resultUuid: this.$props.image.id,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
dl {
  display: flex;
  flex-wrap: wrap;
}

dt {
  @apply font-bold inline-block me-6 w-24;
}

dd {
  width: calc(100% - 92px - 28px);
}
</style>
