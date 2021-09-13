<template>
  <div :aria-label="$t('photo-details.aria.main')" class="audio-page">
    <ClientOnly>
      <AudioTrack :audio="audio" />
    </ClientOnly>
    <template v-if="!$fetchState.pending">
      <MediaReuse
        data-testid="audio-attribution"
        :media="audio"
        :cc-license-u-r-l="ccLicenseURL"
        :full-license-name="fullLicenseName"
        :attribution-html="attributionHtml()"
        class="audio-reuse"
      />
      <AudioDetailsTable
        data-testid="audio-info"
        :audio="audio"
        class="audio-info"
      />
      <AudioDetailsRelated
        v-if="!$fetchState.pending"
        :related-audios="relatedAudios"
        class="audio-related"
      />
    </template>
    <p v-if="$fetchState.pending">Not loaded yet</p>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'
import featureFlags from '~/feature-flags'
import {
  FETCH_AUDIO,
  FETCH_RELATED_MEDIA,
  RESET_RELATED_MEDIA,
} from '~/store-modules/action-types'
import iframeHeight from '~/mixins/iframe-height'
import { AUDIO } from '~/constants/media'
import attributionHtml from '~/utils/attribution-html'
import { getFullLicenseName } from '~/utils/license'

const AudioDetailPage = {
  name: 'AudioDetailPage',
  mixins: [iframeHeight],
  layout({ store }) {
    return store.state.isEmbedded
      ? 'embedded-with-nav-search'
      : 'with-nav-search'
  },
  data() {
    return {
      thumbnailURL: null,
      breadCrumbURL: '',
      shouldShowBreadcrumb: false,
      socialSharingEnabled: featureFlags.socialSharing,
    }
  },
  computed: {
    ...mapState({
      filter: 'query.filter',
      query: 'query',
      tags: 'audio.tags',
      audio: 'audio',
    }),
    relatedAudiosCount() {
      return this.$store.state.related.audios.length
    },
    relatedAudios() {
      return this.$store.state.related.audios
    },
    fullLicenseName() {
      return getFullLicenseName(this.audio.license, this.audio.license_version)
    },
    ccLicenseURL() {
      return `${this.audio.license_url}?ref=ccsearch`
    },
  },
  watch: {
    audio() {
      this.getRelatedAudios()
    },
  },
  async fetch() {
    // Load the related images
    await this[FETCH_RELATED_MEDIA]({
      mediaType: AUDIO,
      id: this.$route.params.id,
    })
  },
  async asyncData({ env, store, route, error, app }) {
    // Clear related audios if present
    await store.dispatch(RESET_RELATED_MEDIA, { mediaType: AUDIO })
    try {
      await store.dispatch(FETCH_AUDIO, { id: route.params.id })
      return {
        thumbnailURL: `${env.apiUrl}thumbs/${route.params.id}`,
        id: route.params.id,
      }
    } catch (err) {
      error({
        statusCode: 404,
        message: app.i18n.t('error.media-not-found', {
          mediaType: AUDIO,
          id: route.params.id,
        }),
      })
    }
  },
  beforeRouteEnter(to, from, nextPage) {
    nextPage((_this) => {
      if (from.path === '/search/' || from.path === '/search/audio') {
        _this.shouldShowBreadcrumb = true
        _this.breadCrumbURL = from.fullPath
      }
    })
  },
  methods: {
    ...mapActions([FETCH_AUDIO, FETCH_RELATED_MEDIA]),
    attributionHtml() {
      const licenseURL = `${this.ccLicenseURL}&atype=html`
      return attributionHtml(this.audio, licenseURL, this.fullLicenseName)
    },
    onAudioLoaded(event) {
      console.log('Image loaded', event)
    },
    getRelatedAudios() {
      console.log('getting related audios id, audio', this.id, this.audio)

      if (this.audio && this.audio.id) {
        this[FETCH_RELATED_MEDIA]({ mediaType: AUDIO, id: this.audio.id })
      }
    },
  },
}

export default AudioDetailPage
</script>
<style lang="scss">
.audio-page {
  --page-margin: 4rem;
  --section-gap: 1.5rem;
  margin-top: var(--section-gap, 1.5rem);
}
// These changes will need to be added in AudioTrack
.info-section {
  padding-left: var(--page-margin, 4rem);
  padding-right: var(--page-margin, 4rem);
  margin-top: var(--section-gap, 1.5rem);
}
.audio-related .info-section {
  padding-left: 0;
  padding-right: 0;
}
.audio-page > section,
.audio-page > aside {
  margin-bottom: var(--page-margin, 4rem);
  margin-top: var(--section-gap, 1.5rem);
  padding-left: var(--page-margin, 4rem);
  padding-right: var(--page-margin, 4rem);
}
</style>
