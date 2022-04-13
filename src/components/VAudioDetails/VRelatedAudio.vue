<template>
  <aside :aria-label="$t('audio-details.related-audios')">
    <h4 class="text-base lg:text-3xl mb-6">
      {{ $t('audio-details.related-audios') }}
    </h4>
    <div v-if="!fetchState.isError" class="flex flex-col gap-8 lg:gap-12 mb-12">
      <VAudioTrack
        v-for="audio in media"
        :key="audio.id"
        :audio="audio"
        layout="row"
        :size="audioTrackSize"
      />
      <LoadingIcon v-show="fetchState.isFetching" />
    </div>
    <p v-show="!!fetchState.isError">
      {{ $t('media-details.related-error') }}
    </p>
  </aside>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'

import { isMinScreen } from '~/composables/use-media-query'

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
    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })
    const audioTrackSize = computed(() => {
      return isMinScreenMd.value ? 'l' : 's'
    })
    return { audioTrackSize }
  },
}
</script>
