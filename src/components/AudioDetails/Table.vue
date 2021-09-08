<template>
  <!--eslint-disable @intlify/vue-i18n/no-raw-text -->
  <section class="audio-info">
    <h4 class="b-header mb-6">Audio information</h4>
    <div class="mb-6 audio-info__grid">
      <img :src="audio.thumbnail" alt="thumbnail" width="110" height="110" />
      <div class="audio-info__data">
        <p>{{ audio.description }}</p>
        <AudioDetailsTags
          :tags="audio.tags"
          :show-header="false"
          class="mt-6 mb-6"
        />
        <dl v-if="audio">
          <div v-if="audio.audio_set">
            <dt>Album</dt>
            <dd>
              <a :href="audio.audio_set.url">{{ audio.audio_set.name }}</a>
            </dd>
          </div>
          <div>
            <dt>
              {{ $t('media-details.provider-label') }}
            </dt>
            <dd>
              {{ providerName }}
            </dd>
          </div>
          <div v-if="audio.genres">
            <dt>
              {{ $t('audio-details.genre-label') }}
            </dt>
            <dd>
              {{ audio.genres.join(', ') }}
            </dd>
          </div>
          <div>
            <dt>
              {{ $t('media-details.source-label') }}
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
          </div>
        </dl>
      </div>
    </div>
  </section>
</template>

<script>
import {
  SEND_DETAIL_PAGE_EVENT,
  DETAIL_PAGE_EVENTS,
} from '~/store-modules/usage-data-analytics-types'
import getProviderName from '~/utils/get-provider-name'
import getProviderLogo from '~/utils/get-provider-logo'

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
        resultUuid: this.$props.audio.id,
      })
    },
  },
}
</script>

<style lang="scss" scoped>
.audio-info__grid {
  display: grid;
  grid-template-columns: 110px auto;
  grid-template-rows: repeat(auto-fit, 1fr);
  grid-gap: 1.5rem;
}
dl {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
}
dl div {
  display: flex;
  flex-direction: column;
  padding-left: 1rem;
  padding-right: 1rem;
}

dt {
  font-weight: 400;
  display: inline-block;
}

dd {
  font-weight: bold;
}
</style>
