<template>
  <aside :aria-label="$t('audio-details.related-audios')">
    <h2 class="heading-6 lg:heading-6 mb-6">
      {{ $t("audio-details.related-audios") }}
    </h2>
    <!-- Negative margin compensates for the `p-4` padding in row layout. -->
    <div
      v-if="!fetchState.fetchingError"
      class="-mx-2 mb-12 flex flex-col gap-4 md:-mx-4"
    >
      <VAudioTrack
        v-for="audio in media"
        :key="audio.id"
        :audio="audio"
        layout="row"
        :size="audioTrackSize"
      />
      <LoadingIcon v-show="fetchState.isFetching" />
    </div>
    <p v-show="!!fetchState.fetchingError">
      {{ $t("media-details.related-error") }}
    </p>
  </aside>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "@nuxtjs/composition-api"

import { useUiStore } from "~/stores/ui"

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

    const audioTrackSize = computed(() => {
      return uiStore.isBreakpoint("md") ? "l" : "s"
    })

    return { audioTrackSize }
  },
})
</script>
