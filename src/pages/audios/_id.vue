<template>
  <div :aria-label="$t('photo-details.aria.main')">
    <!--<AudioTrack :audio="audio" />-->
    <section v-if="!$fetchState.pending" class="audio-page">
      <h4 class="b-header mb-6">Reuse Content</h4>
      <AudioAttribution
        data-testid="audio-attribution"
        :audio="audio"
        :cc-license-u-r-l="ccLicenseURL"
        :full-license-name="fullLicenseName"
        :attribution-html="attributionHtml()"
      />
      <AudioInfo data-testid="audio-info" :audio="audio" />
      <AudioTags :tags="tags" header="" class="p-4 my-6" />
      <RelatedAudios
        v-if="!$fetchState.pending"
        :related-audios="relatedAudios"
        :audios-count="relatedAudiosCount"
        :query="query"
        :filter="filter"
      />
    </section>
    <p v-else>Not loaded yet</p>
  </div>
</template>

<script>
import { mapActions, mapMutations, mapState } from 'vuex'
import featureFlags from '~/featureFlags'
import { FETCH_AUDIO, FETCH_RELATED_MEDIA } from '~/store-modules/action-types'
import { SET_AUDIO, SET_RELATED_MEDIA } from '~/store-modules/mutation-types'
import iframeHeight from '~/mixins/iframeHeight'
import { AUDIO } from '~/constants/media'
import attributionHtml from '~/utils/attributionHtml'

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
      const license = this.audio.license
      const version = this.audio.license_version

      if (license) {
        return license.toLowerCase() === 'cc0'
          ? `${license} ${version}`
          : `CC ${license} ${version}`
      }
      return ''
    },
    ccLicenseURL() {
      return `${this.audio.license_url}?ref=ccsearch`
    },
  },
  watch: {
    audio() {
      console.log('audio changed')
      this.getRelatedAudios()
    },
  },
  mounted() {
    console.log(JSON.stringify(this.audio, null, 2))
  },
  async fetch() {
    try {
      // Load the related images in parallel
      await this.$store.dispatch(FETCH_RELATED_MEDIA, {
        mediaType: AUDIO,
        id: this.$route.params.id,
      })
      setTimeout(() => {
        console.log('timeout over')
      }, 5000)
    } catch (err) {
      console.log('oops, ', err)
      // this.$error({
      //   statusCode: 404,
      //   message: app.i18n.t('error.image-not-found', { id: route.params.id }),
      // })
    }
  },
  async asyncData({ env, store, route, error, app }) {
    // Clear related audios if present
    if (store.state.related.audios && store.state.related.audios.length > 0) {
      store.commit(SET_RELATED_MEDIA, {
        mediaType: AUDIO,
        relatedMedia: [],
      })
    }
    try {
      await store.dispatch(FETCH_AUDIO, { id: route.params.id })
      return {
        thumbnailURL: `${env.apiUrl}thumbs/${route.params.id}`,
      }
    } catch (err) {
      console.log('oops, ', err)
      error({
        statusCode: 404,
        message: app.i18n.t('error.image-not-found', { id: route.params.id }),
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
    ...mapMutations([SET_AUDIO]),
    attributionHtml() {
      const licenseURL = `${this.ccLicenseURL}&atype=html`
      return attributionHtml(this.audio, licenseURL, this.fullLicenseName)
    },
    onAudioLoaded(event) {
      console.log('Image loaded', event)
    },
    getRelatedAudios() {
      console.log('id', this.id, this.audio)

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
  padding-left: var(--page-margin, 4rem);
  padding-right: var(--page-margin, 4rem);
}
.info-section {
  padding-left: var(--page-margin, 4rem);
  padding-right: var(--page-margin, 4rem);
  margin-top: var(--section-gap, 1.5rem);
}
.audio-info {
}
</style>
