<template>
  <div :aria-label="$t('photo-details.aria.main')" class="audio-page">
    <AudioTrack :audio="audio" class="main-track" />
    <MediaReuse
      data-testid="audio-attribution"
      :media="audio"
      :license-url="licenseUrl"
      :full-license-name="fullLicenseName"
      :attribution-html="attributionHtml()"
      class="my-16 px-4 tab:px-0"
    />
    <AudioDetailsTable
      data-testid="audio-info"
      :audio="audio"
      class="my-16 px-4 desk:px-0"
    />
    <AudioDetailsRelated
      v-if="audio.id"
      class="my-16 px-4 desk:px-0"
      :audio-id="audio.id"
    />
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'
import { FETCH_AUDIO } from '~/constants/action-types'
import iframeHeight from '~/mixins/iframe-height'
import { AUDIO } from '~/constants/media'
import attributionHtml from '~/utils/attribution-html'
import { getFullLicenseName } from '~/utils/license'

const AudioDetailPage = {
  name: 'AudioDetailPage',
  mixins: [iframeHeight],
  layout({ store }) {
    return store.state.nav.isEmbedded
      ? 'embedded-with-nav-search'
      : 'with-nav-search'
  },
  data() {
    return {
      thumbnailURL: null,
      breadCrumbURL: '',
      shouldShowBreadcrumb: false,
      id: null,
    }
  },
  computed: {
    ...mapState(['audio']),
    fullLicenseName() {
      return getFullLicenseName(this.audio.license, this.audio.license_version)
    },
    licenseUrl() {
      return `${this.audio.license_url}?ref=openverse`
    },
  },
  watch: {
    audio(newAudio) {
      this.id = newAudio.id
    },
  },
  async asyncData({ env, store, route, error, app }) {
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
    ...mapActions([FETCH_AUDIO]),
    attributionHtml() {
      const licenseUrl = `${this.licenseUrl}&atype=html`
      return attributionHtml(this.audio, licenseUrl, this.fullLicenseName)
    },
  },
}

export default AudioDetailPage
</script>
<style>
.audio-page {
  --wp-max-width: 940px;
}
.audio-page section,
.audio-page aside {
  max-width: var(--wp-max-width);
  margin-right: auto;
  margin-left: auto;
}
.audio-page .full-track .mx-16 {
  @apply mt-6;
  @apply px-4 tab:px-0;
  max-width: var(--wp-max-width);
  margin-right: auto;
  margin-left: auto;
}
</style>
