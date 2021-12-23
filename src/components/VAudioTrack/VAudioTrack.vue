<template>
  <div
    class="audio-track"
    :aria-label="$t('audio-track.aria-label')"
    role="region"
  >
    <Component :is="layoutComponent" :audio="audio" :size="size">
      <template #controller="controllerProps">
        <VAudioController
          v-model="status"
          v-bind="controllerProps"
          :audio="audio"
          @ready="handleReady"
          @finished="handleFinished"
          @seeked="handleSeeked"
        />
      </template>

      <template #play-pause="playPauseProps">
        <VPlayPause
          v-model="status"
          v-bind="playPauseProps"
          :disabled="!isReady"
        />
      </template>
    </Component>
  </div>
</template>

<script>
import { computed, defineComponent, ref } from '@nuxtjs/composition-api'

import VPlayPause from '~/components/VAudioTrack/VPlayPause.vue'
import VAudioController from '~/components/VAudioTrack/VAudioController.vue'

import VFullLayout from '~/components/VAudioTrack/layouts/VFullLayout.vue'
import VRowLayout from '~/components/VAudioTrack/layouts/VRowLayout.vue'
import VBoxLayout from '~/components/VAudioTrack/layouts/VBoxLayout.vue'
import VGlobalLayout from '~/components/VAudioTrack/layouts/VGlobalLayout.vue'

/**
 * Displays the waveform and basic information about the track, along with
 * controls to play, pause or seek to a point on the track.
 */
export default defineComponent({
  name: 'VAudioTrack',
  components: {
    VAudioController,
    VPlayPause,

    // Layouts
    VFullLayout,
    VRowLayout,
    VBoxLayout,
    VGlobalLayout,
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
      full: 'VFullLayout',
      row: 'VRowLayout',
      box: 'VBoxLayout',
      global: 'VGlobalLayout',
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
})
</script>
