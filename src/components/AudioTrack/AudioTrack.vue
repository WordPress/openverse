<template>
  <div
    class="audio-track"
    :aria-label="$t('audio-track.aria-label')"
    role="region"
  >
    <Component :is="layoutComponent" :audio="audio" :size="size">
      <template #controller="controllerProps">
        <AudioController
          v-model="status"
          v-bind="controllerProps"
          :audio="audio"
          @ready="handleReady"
          @finished="handleFinished"
          @seeked="handleSeeked"
        />
      </template>

      <template #play-pause="playPauseProps">
        <PlayPause
          v-model="status"
          v-bind="playPauseProps"
          :disabled="!isReady"
        />
      </template>
    </Component>
  </div>
</template>

<script>
import { computed, ref } from '@nuxtjs/composition-api'

import PlayPause from '~/components/AudioTrack/PlayPause.vue'
import AudioController from '~/components/AudioTrack/AudioController.vue'

import Full from '~/components/AudioTrack/layouts/Full.vue'
import Row from '~/components/AudioTrack/layouts/Row.vue'
import Box from '~/components/AudioTrack/layouts/Box.vue'
import Global from '~/components/AudioTrack/layouts/Global.vue'

/**
 * Displays the waveform and basic information about the track, along with
 * controls to play, pause or seek to a point on the track.
 */
export default {
  name: 'AudioTrack',
  components: {
    AudioController,
    PlayPause,

    // Layouts
    Full,
    Row,
    Box,
    Global,
  },
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
      validator: (val) => ['full', 'box', 'row', 'global'].includes(val),
    },
    /**
     * the size of the component; Both 'box' and 'row' layouts offer multiple
     * sizes to choose from.
     */
    size: {
      type: String,
      default: 'm',
      validator: (val) => ['s', 'm', 'l'].includes(val),
    },
  },
  setup(props) {
    /* Status */

    const status = ref('paused')

    const handleSeeked = () => {
      if (status.value === 'played') {
        status.value = 'paused'
      }
    }
    const handleFinished = () => {
      status.value = 'played'
    }

    /* Metadata readiness */

    const isReady = ref(false)
    const handleReady = () => {
      isReady.value = true
    }

    /* Layout */

    const layoutMappings = {
      full: 'Full',
      row: 'Row',
      box: 'Box',
      global: 'Global',
    }
    const layoutComponent = computed(() => layoutMappings[props.layout])

    return {
      status,
      handleSeeked,
      handleFinished,

      isReady,
      handleReady,

      layoutComponent,
    }
  },
}
</script>
