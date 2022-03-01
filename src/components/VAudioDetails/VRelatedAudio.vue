<template>
  <aside :aria-label="$t('audio-details.related-audios')">
    <h4 class="text-base lg:text-3xl mb-6">
      {{ $t('audio-details.related-audios') }}
    </h4>
    <div v-if="!$fetchState.error" class="flex flex-col gap-8 lg:gap-12 mb-12">
      <VAudioTrack
        v-for="audio in audios"
        :key="audio.id"
        :audio="audio"
        layout="row"
        :size="audioTrackSize"
      />
      <LoadingIcon v-show="$fetchState.pending" />
    </div>
    <p v-show="!!$fetchState.error">
      {{ $t('media-details.related-error') }}
    </p>
  </aside>
</template>

<script>
import { computed, ref } from '@nuxtjs/composition-api'

import { AUDIO } from '~/constants/media'

import useRelated from '~/composables/use-related'
import { isMinScreen } from '~/composables/use-media-query'

import LoadingIcon from '~/components/LoadingIcon.vue'

import VAudioTrack from '~/components/VAudioTrack/VAudioTrack.vue'

export default {
  name: 'VRelatedAudio',
  components: { VAudioTrack, LoadingIcon },
  props: {
    audioId: {
      type: String,
      required: true,
    },
    service: {},
  },
  /**
   * Fetches related audios on `audioId` change
   * @param {object} props
   * @param {string} props.audioId
   * @param {any} props.service
   * @return {{ audios: import('~/composables/types').Ref<import('~/store/types').AudioDetail[]>, audioTrackSize: import('@nuxtjs/composition-api').ComputedRef<"l" | "s"> }}
   */
  setup(props) {
    const mainAudioId = ref(props.audioId)
    const relatedOptions = {
      mediaType: AUDIO,
      mediaId: mainAudioId,
      service: undefined,
    }
    // Using service prop to be able to mock when testing
    if (props.service) {
      relatedOptions.service = props.service
    }

    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })
    const audioTrackSize = computed(() => {
      return isMinScreenMd.value ? 'l' : 's'
    })

    const { media: audios } = useRelated(relatedOptions)
    return { audioTrackSize, audios }
  },
}
</script>
