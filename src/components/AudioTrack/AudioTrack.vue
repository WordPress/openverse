<template>
  <div
    class="audio-track"
    :aria-label="$t('audio-track.aria-label')"
    role="region"
  >
    <Component
      :is="layoutComponent"
      :audio="audio"
      :size="size"
      :aspect="aspect"
    >
      <template #controller>
        <AudioController v-model="status" :audio="audio" @ready="handleReady" />
      </template>

      <template #play-pause>
        <PlayPause v-model="status" :disabled="!isReady" />
      </template>
    </Component>
  </div>
</template>

<script>
import { computed, ref } from '@nuxtjs/composition-api'
import PlayPause from '~/components/AudioTrack/PlayPause.vue'
import AudioController from '~/components/AudioTrack/AudioController.vue'
import Full from '~/components/AudioTrack/layouts/Full.vue'

/**
 * Displays the waveform and basic information about the track, along with
 * controls to play, pause or seek to a point on the track.
 */
export default {
  name: 'AudioTrack',
  components: { AudioController, PlayPause, Full },
  props: {
    /**
     * the information about the track, typically from a track's detail endpoint
     */
    audio: {
      type: Object,
      required: true,
    },
    /**
     * the arrangement of the contents on the canvas; This determines the
     * overall L&F of the audio component.
     */
    layout: {
      type: String,
      default: 'full',
      validator: (val) => ['full', 'box', 'row'].includes(val),
    },
    /**
     * the size of the component; Both 'box' and 'row' layouts offer multiple
     * sizes to choose from.
     */
    size: {
      type: String,
      default: 'm',
      validator: (val) => ['s', 'm', 'l', 'xl'].includes(val),
    },
    /**
     * whether to show the 'box' layout with a wider aspect ratio; This is
     * opposed to the regular square layout.
     */
    aspect: {
      type: String,
      default: 'regular',
      validator: (val) => ['regular', 'wide'].includes(val),
    },
  },
  setup(props) {
    /* Status */

    const status = ref('paused')

    /* Metadata readiness */

    const isReady = ref(false)
    const handleReady = () => {
      isReady.value = true
    }

    /* Layout */

    const layoutComponent = computed(() => {
      if (props.layout === 'full') {
        return 'Full'
      }
    })

    return {
      status,

      isReady,
      handleReady,

      layoutComponent,
    }
  },
}
</script>
