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
import { computed, defineComponent, useRoute } from '@nuxtjs/composition-api'

import { AUDIO } from '~/constants/media'
import type { AudioDetail } from '~/models/media'
import { useRelatedMediaStore } from '~/stores/media/related-media'
import { useSingleResultStore } from '~/stores/media/single-result'
import { createDetailPageMeta } from '~/utils/og'

import VAudioDetails from '~/components/VAudioDetails/VAudioDetails.vue'
import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'
import VBackToSearchResultsLink from '~/components/VBackToSearchResultsLink.vue'
import VRelatedAudio from '~/components/VAudioDetails/VRelatedAudio.vue'
import VMediaReuse from '~/components/VMediaInfo/VMediaReuse.vue'

export default defineComponent({
  name: 'AudioDetailPage',
  components: {
    VAudioDetails,
    VAudioTrack,
    VBackToSearchResultsLink,
    VMediaReuse,
    VRelatedAudio,
  },
  beforeRouteEnter(to, from, next) {
    if (from.path.includes('/search/')) {
      to.meta.backToSearchPath = from.fullPath
    }
    next()
  },
  setup() {
    const route = useRoute()
    const singleResultStore = useSingleResultStore()
    const relatedMediaStore = useRelatedMediaStore()

    const audio = computed(() =>
      singleResultStore.mediaType === AUDIO
        ? (singleResultStore.mediaItem as AudioDetail)
        : null
    )
    const relatedMedia = computed(() => relatedMediaStore.media)
    const relatedFetchState = computed(() => relatedMediaStore.fetchState)
    const backToSearchPath = computed(() => route.value.meta?.backToSearchPath)

    return { audio, backToSearchPath, relatedMedia, relatedFetchState }
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
  head() {
    return createDetailPageMeta(this.audio.title, this.audio.thumbnail)
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
