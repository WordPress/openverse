<template>
  <aside :aria-label="$t('audio-details.related-audios')">
    <h2 class="heading-6 lg:heading-6 mb-6">
      {{ $t("audio-details.related-audios") }}
    </h2>
    <!-- Negative margin compensates for the `p-4` padding in row layout. -->
    <ol
      v-if="!fetchState.fetchingError"
      :aria-label="$t('audio-details.related-audios')"
      class="-mx-2 mb-12 flex flex-col gap-4 md:-mx-4"
    >
      <li v-for="audio in media" :key="audio.id">
        <VAudioTrack
          :audio="audio"
          layout="row"
          :size="audioTrackSize"
          @mousedown="sendSelectSearchResultEvent(audio)"
        />
      </li>
    </ol>
    <LoadingIcon
      v-if="!fetchState.fetchingError"
      v-show="fetchState.isFetching"
    />
    <p v-show="!!fetchState.fetchingError">
      {{ $t("media-details.related-error") }}
    </p>
  </aside>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useUiStore } from "~/stores/ui"

import { useSearchStore } from "~/stores/search"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { useAnalytics } from "~/composables/use-analytics"
import { AUDIO } from "~/constants/media"

import type { FetchState } from "~/models/fetch-state"
import type { AudioDetail } from "~/models/media"

import LoadingIcon from "~/components/LoadingIcon.vue"
import VAudioTrack from "~/components/VAudioTrack/VAudioTrack.vue"

export default defineComponent({
  name: "VRelatedAudio",
  components: { VAudioTrack, LoadingIcon },
  props: {
    media: {
      type: Array as PropType<AudioDetail>,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState>,
      required: true,
    },
  },
  setup() {
    const uiStore = useUiStore()
    const relatedMediaStore = useRelatedMediaStore()

    const audioTrackSize = computed(() => {
      return uiStore.isBreakpoint("md") ? "l" : "s"
    })

    const { sendCustomEvent } = useAnalytics()
    const sendSelectSearchResultEvent = (audio: AudioDetail) => {
      sendCustomEvent("SELECT_SEARCH_RESULT", {
        id: audio.id,
        relatedTo: relatedMediaStore.mainMediaId,
        mediaType: AUDIO,
        provider: audio.provider,
        query: useSearchStore().searchTerm,
      })
    }

    return { audioTrackSize, sendSelectSearchResultEvent }
  },
})
</script>
