<template>
  <div class="audio-controller">
    <Waveform
      :class="waveformClasses"
      :message="message ? $t(`audio-track.messages.${message}`) : null"
      :current-time="currentTime"
      :duration="duration"
      :peaks="audio.peaks"
      @seeked="handleSeeked"
    />

    <!-- eslint-disable vuejs-accessibility/media-has-caption -->
    <audio
      v-show="false"
      v-bind="$attrs"
      :id="audio.id"
      ref="audioEl"
      class="audio-controller"
      controls
      :src="audio.url"
      crossorigin="anonymous"
      @loadedmetadata="handleReady"
      @error="handleError"
    />
    <!-- eslint-enable vuejs-accessibility/media-has-caption -->
  </div>
</template>

<script>
import Waveform from '~/components/AudioTrack/Waveform'
import { computed, ref, useStore, watch } from '@nuxtjs/composition-api'
import {
  SET_ACTIVE_MEDIA_ITEM,
  UNSET_ACTIVE_MEDIA_ITEM,
} from '~/constants/mutation-types'

/**
 * Controls the interaction between the parent Vue component, the underlying
 * HTMLAudioElement and the Active Media Store. Also displays the waveform that
 * is deeply linked to timekeeping for the HTMLAudioElement.
 */
export default {
  name: 'AudioController',
  components: { Waveform },
  inheritAttrs: false,
  model: {
    prop: 'status',
    event: 'change',
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
     * the playing/paused status of the audio
     */
    status: {
      type: String,
      required: true,
      validator: (val) => ['playing', 'paused'].includes(val),
    },
    /**
     * the CSS classes to apply on the waveform; This can take any form
     * acceptable to Vue class bindings.
     */
    waveformClasses: {},
  },
  setup(props, { emit }) {
    const store = useStore()

    const audioEl = ref(null) // template ref

    /* Status */

    const isActiveTrack = computed(
      () =>
        store.state['active-media'].type === 'audio' &&
        store.state['active-media'].id === props.audio.id
    )
    // Sync status from parent to player and store
    watch(
      () => props.status,
      (status) => {
        if (!audioEl.value) return

        switch (status) {
          case 'playing':
            audioEl.value.play()
            store.commit(SET_ACTIVE_MEDIA_ITEM, {
              type: 'audio',
              id: props.audio.id,
            })
            window.requestAnimationFrame(updateTimeLoop)
            break
          case 'paused':
            audioEl.value.pause()
            if (isActiveTrack.value) {
              store.commit(UNSET_ACTIVE_MEDIA_ITEM)
            }
            break
        }
      }
    )
    // Sync status from store to parent
    watch(
      () => [store.state['active-media'].type, store.state['active-media'].id],
      () => {
        const status = isActiveTrack.value ? 'playing' : 'paused'
        emit('change', status)
      }
    )

    /* Error handling */

    const message = ref('loading')
    const handleError = (event) => {
      const error = event.target.error
      let errorMsg
      switch (error.code) {
        case error.MEDIA_ERR_ABORTED:
          errorMsg = 'err_aborted'
          break
        case error.MEDIA_ERR_NETWORK:
          errorMsg = 'err_network'
          break
        case error.MEDIA_ERR_DECODE:
          errorMsg = 'err_decode'
          break
        case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
          errorMsg = 'err_unsupported'
          break
      }
      message.value = errorMsg
    }

    /* Timekeeping */

    const currentTime = ref(0)
    const duration = ref(0)
    const updateTime = () => {
      if (!audioEl.value) return

      currentTime.value = audioEl.value.currentTime
      duration.value = audioEl.value.duration
    }
    const updateTimeLoop = () => {
      updateTime()
      if (props.status === 'playing') {
        // Audio is playing, keep looping
        window.requestAnimationFrame(updateTimeLoop)
      }
    }

    /* Metadata readiness */

    const handleReady = () => {
      message.value = null
      updateTime()
      emit('ready')
    }

    /* Seeking */

    const handleSeeked = (frac) => {
      if (audioEl.value && duration.value) {
        audioEl.value.currentTime = duration.value * frac
        updateTime()
      }
    }

    return {
      audioEl,

      message,
      handleError,

      currentTime,
      duration,

      handleReady,

      handleSeeked,
    }
  },
}
</script>
