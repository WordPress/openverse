<template>
  <main class="relative">
    <div class="w-full p-2">
      <VBackToSearchResultsLink />
    </div>
    <VAudioTrack layout="full" :audio="audio" class="main-track" />
    <div
      class="mt-10 lg:mt-16 flex flex-col gap-10 lg:gap-16 px-4 lg:px-0 lg:max-w-5xl mx-auto"
    >
      <VMediaReuse
        data-testid="audio-attribution"
        :media="audio"
        :license-url="licenseUrl"
        :full-license-name="fullLicenseName"
        :attribution-html="attributionHtml()"
      />
      <VAudioDetails data-testid="audio-info" :audio="audio" />
      <VRelatedAudio v-if="audio.id" :audio-id="audio.id" />
    </div>
  </main>
</template>

<script>
import { mapState } from 'vuex'

import { FETCH_MEDIA_ITEM } from '~/constants/action-types'
import { AUDIO } from '~/constants/media'
import getAttributionHtml from '~/utils/attribution-html'
import { getFullLicenseName } from '~/utils/license'
import { MEDIA } from '~/constants/store-modules'

const AudioDetailPage = {
  name: 'AudioDetailPage',
  data() {
    return {
      showBackToSearchLink: false,
    }
  },
  computed: {
    ...mapState(MEDIA, ['audio']),
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
  async asyncData({ store, route, error, app }) {
    try {
      await store.dispatch(`${MEDIA}/${FETCH_MEDIA_ITEM}`, {
        id: route.params.id,
        mediaType: AUDIO,
      })
      return {
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
      if (
        from.name === _this.localeRoute({ path: '/search/' }).name ||
        from.name === _this.localeRoute({ path: '/search/audio' }).name
      ) {
        _this.showBackToSearchLink = true
      }
    })
  },
  methods: {
    attributionHtml() {
      const licenseUrl = `${this.licenseUrl}&atype=html`
      return getAttributionHtml(this.audio, licenseUrl, this.fullLicenseName)
    },
  },
  head() {
    const title = this.audio.title
    return {
      title: `${title} | Openverse`,
      meta: [
        {
          hid: 'robots',
          name: 'robots',
          content: 'noindex',
        },
      ],
    }
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
  @apply px-4 md:px-0;
  max-width: var(--wp-max-width);
  margin-right: auto;
  margin-left: auto;
}
</style>
