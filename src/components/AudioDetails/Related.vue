<template>
  <aside :aria-label="$t('photo-details.aria.related')">
    <h4 class="b-header mb-6">
      {{ $t('audio-details.related-audios') }}
    </h4>
    <template v-if="!$fetchState.error">
      <VAudioTrack
        v-for="audio in audios"
        :key="audio.id"
        :audio="audio"
        layout="row"
        size="m"
        class="mb-12"
      />
      <LoadingIcon v-show="$fetchState.pending" />
    </template>
    <p v-show="!!$fetchState.error">
      {{ $t('media-details.related-error') }}
    </p>
  </aside>
</template>

<script>
import { ref } from '@nuxtjs/composition-api'
import { AUDIO } from '~/constants/media'
import useRelated from '~/composables/use-related'

export default {
  name: 'RelatedAudios',
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
   * @return {{ audios: Ref<AudioDetail[]> }}
   */
  setup(props) {
    const mainAudioId = ref(props.audioId)
    const relatedOptions = {
      mediaType: AUDIO,
      mediaId: mainAudioId,
    }
    // Using service prop to be able to mock when testing
    if (props.service) {
      relatedOptions.service = props.service
    }
    const { media: audios } = useRelated(relatedOptions)
    return { audios }
  },
}
</script>
