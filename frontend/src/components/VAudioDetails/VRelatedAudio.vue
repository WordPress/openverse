<template>
  <aside :aria-label="$t('audioDetails.relatedAudios')">
    <h2 class="heading-6 lg:heading-6 mb-6">
      {{ $t("audioDetails.relatedAudios") }}
    </h2>
    <!-- Negative margin compensates for the `p-4` padding in row layout. -->
    <ol
      v-if="!fetchState.fetchingError"
      :aria-label="$t('audioDetails.relatedAudios')"
      class="-mx-2 mb-12 flex flex-col gap-4 md:-mx-4"
    >
      <li v-for="audio in media" :key="audio.id">
        <VAudioTrack :audio="audio" layout="row" :size="audioTrackSize" />
      </li>
    </ol>
    <LoadingIcon
      v-if="!fetchState.fetchingError"
      v-show="fetchState.isFetching"
    />
    <p v-show="!!fetchState.fetchingError">
      {{ $t("mediaDetails.relatedError") }}
    </p>
  </aside>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

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
