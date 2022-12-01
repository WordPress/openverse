<template>
  <aside :aria-label="$t('audio-details.related-audios')">
    <h2 class="mb-6 text-2xl lg:text-3xl">
      {{ $t('audio-details.related-audios') }}
    </h2>
    <!-- Negative margin compensates for the `p-4` padding in row layout. -->
    <div
      v-if="!fetchState.fetchingError"
      class="-mx-4 mb-12 flex flex-col gap-4"
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
      {{ $t('media-details.related-error') }}
    </p>
  </aside>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'

import { useUiStore } from '~/stores/ui'

import LoadingIcon from '~/components/LoadingIcon.vue'
import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'

export default {
  name: 'VRelatedAudio',
  components: { VAudioTrack, LoadingIcon },
  props: {
    media: {
      type: Array,
      required: true,
    },
    fetchState: {
      type: Object,
      required: true,
    },
  },
  /**
   * Fetches related audios on `audioId` change
   * @return {{audioTrackSize: import('@nuxtjs/composition-api').ComputedRef<"l" | "s"> }}
   */
  setup() {
    const uiStore = useUiStore()

    const audioTrackSize = computed(() => {
      return uiStore.isBreakpoint('md') ? 'l' : 's'
    })

    return { audioTrackSize }
  },
}
</script>
