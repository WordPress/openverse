<template>
  <!--eslint-disable @intlify/vue-i18n/no-raw-text -->
  <section class="audio-info">
    <h4 class="b-header mb-6">Audio information</h4>
    <div class="mb-6 audio-info__grid">
      <img :src="audio.thumbnail" alt="thumbnail" />
      <div class="audio-info__data">
        <p>{{ audio.description }}</p>
        <dl>
          <dt class="mb-2">
            {{ $t('photo-details.information.dimensions') }}
          </dt>
          <dt v-if="providerName !== sourceName" class="mb-2">
            {{ $t('photo-details.information.provider') }}
          </dt>
          <dd v-if="providerName !== sourceName">
            {{ providerName }}
          </dd>
          <dt class="mb-2">
            {{ $t('photo-details.information.source') }}
          </dt>
          <dd>
            <a
              :aria-label="sourceName"
              :href="audio.foreign_landing_url"
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
    </div>
    <div class="mb-6">
      <h5 class="mb-2 b-header">
        {{ $t('photo-details.information.tags') }}
      </h5>
      <AudioTags :tags="audio.tags" :show-header="false" />
    </div>
  </section>
</template>

<script>
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/store-modules/usage-data-analytics-types'
import getProviderName from '~/utils/getProviderName'
import getProviderLogo from '~/utils/getProviderLogo'

export default {
  name: 'AudioInfo',
  props: ['audio', 'ccLicenseURL', 'fullLicenseName'],
  data: () => ({
    fields: [
      'album',
      'category',
      'mood',
      'sample_rate',
      'language',
      'format',
      'source',
      'upload_date',
    ],
  }),
  computed: {
    providerName() {
      return getProviderName(
        this.$store.state.audioProviders,
        this.$props.audio.provider
      )
    },
    sourceName() {
      return getProviderName(
        this.$store.state.audioProviders,
        this.$props.audio.source
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
.audio-info__grid {
  display: grid;
  grid-template-columns: 110px 1fr;
  grid-gap: 2rem;
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
