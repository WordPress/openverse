<template>
  <main class="relative">
    <div v-if="backToSearchPath" class="w-full p-2">
      <VBackToSearchResultsLink :path="backToSearchPath" />
    </div>
    <VAudioTrack layout="full" :audio="audio" class="main-track" />
    <div
      class="mt-10 lg:mt-16 flex flex-col gap-10 lg:gap-16 px-4 lg:px-0 lg:max-w-5xl mx-auto"
    >
      <VMediaReuse data-testid="audio-attribution" :media="audio" />
      <VAudioDetails data-testid="audio-info" :audio="audio" />
      <VRelatedAudio
        v-if="audio.id"
        :media="relatedMedia"
        :fetch-state="relatedFetchState"
      />
    </div>
  </main>
</template>

<script lang="ts">
import { computed, defineComponent } from '@nuxtjs/composition-api'

import { AUDIO } from '~/constants/media'
import type { AudioDetail } from '~/models/media'
import { useRelatedMediaStore } from '~/stores/media/related-media'
import { useSingleResultStore } from '~/stores/media/single-result'

import VAudioDetails from '~/components/VAudioDetails/VAudioDetails.vue'
import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'
import VBackToSearchResultsLink from '~/components/VBackToSearchResultsLink.vue'
import VRelatedAudio from '~/components/VAudioDetails/VRelatedAudio.vue'
import VMediaReuse from '~/components/VMediaInfo/VMediaReuse.vue'

import type { NuxtApp } from '@nuxt/types/app'

export default defineComponent({
  name: 'AudioDetailPage',
  components: {
    VAudioDetails,
    VAudioTrack,
    VBackToSearchResultsLink,
    VMediaReuse,
    VRelatedAudio,
  },
  beforeRouteEnter(to, from, nextPage) {
    nextPage((_this) => {
      // `_this` is the component instance that also has nuxt app properties injected
      const localeRoute = (_this as NuxtApp).localeRoute
      if (
        from.name === localeRoute({ path: '/search/' }).name ||
        from.name === localeRoute({ path: '/search/audio' }).name
      ) {
        // I don't know how to type `_this` here
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        _this.backToSearchPath = from.fullPath
      }
    })
  },
  setup() {
    const singleResultStore = useSingleResultStore()
    const relatedMediaStore = useRelatedMediaStore()

    const audio = computed(() =>
      singleResultStore.mediaType === AUDIO
        ? (singleResultStore.mediaItem as AudioDetail)
        : null
    )
    const relatedMedia = computed(() => relatedMediaStore.media)
    const relatedFetchState = computed(() => relatedMediaStore.fetchState)

    return { audio, relatedMedia, relatedFetchState }
  },
  async asyncData({ route, error, app, $pinia }) {
    const audioId = route.params.id
    const singleResultStore = useSingleResultStore($pinia)

    try {
      await singleResultStore.fetch(AUDIO, audioId)
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
  data() {
    return {
      backToSearchPath: '',
    }
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
})
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
