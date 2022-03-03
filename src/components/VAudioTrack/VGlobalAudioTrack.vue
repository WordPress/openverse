<template>
  <div
    class="audio-track"
    :aria-label="$t('audio-track.aria-label')"
    role="region"
  >
    <Component :is="layoutComponent" :audio="audio" :size="size">
      <template #controller="waveformProps">
        <VWaveform
          v-bind="waveformProps"
          :peaks="audio.peaks"
          :current-time="currentTime"
          :duration="duration"
          :message="message ? $t(`audio-track.messages.${message}`) : null"
          @seeked="handleSeeked"
          @toggle-playback="handleToggle"
        />
      </template>

      <template #play-pause="playPauseProps">
        <VPlayPause
          :status="status"
          v-bind="playPauseProps"
          @toggle="handleToggle"
        />
      </template>
    </Component>
  </div>
</template>

<script>
import { computed, defineComponent, ref, watch } from '@nuxtjs/composition-api'

import { useActiveAudio } from '~/composables/use-active-audio'

import { useActiveMediaStore } from '~/stores/active-media'

import VPlayPause from '~/components/VAudioTrack/VPlayPause.vue'
import VWaveform from '~/components/VAudioTrack/VWaveform.vue'

import VFullLayout from '~/components/VAudioTrack/layouts/VFullLayout.vue'
import VRowLayout from '~/components/VAudioTrack/layouts/VRowLayout.vue'
import VBoxLayout from '~/components/VAudioTrack/layouts/VBoxLayout.vue'
import VGlobalLayout from '~/components/VAudioTrack/layouts/VGlobalLayout.vue'

const propTypes = {
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
   * @todo This type def should be extracted for reuse across components
   */
  layout: {
    type: /** @type {import('@nuxtjs/composition-api').PropType<'full' | 'box' | 'row' | 'global'>} */ (
      String
    ),
    default: 'full',
    /**
     * @param {string} val
     */
    validator: (val) => ['full', 'box', 'row', 'global'].includes(val),
  },
  /**
   * the size of the component; Both 'box' and 'row' layouts offer multiple
   * sizes to choose from.
   */
  size: {
    type: /** @type {import('@nuxtjs/composition-api').PropType<'s' | 'm' | 'l'>} */ (
      String
    ),
    default: 'm',
    /**
     * @param {string} val
     */
    validator: (val) => ['s', 'm', 'l'].includes(val),
  },
}

/**
 * Displays the waveform and basic information about the track, along with
 * controls to play, pause or seek to a point on the track.
 */
export default defineComponent({
  name: 'VGlobalAudioTrack',
  components: {
    VPlayPause,
    VWaveform,

    // Layouts
    VFullLayout,
    VRowLayout,
    VBoxLayout,
    VGlobalLayout,
  },
  props: propTypes,
  /**
   * @param {import('@nuxtjs/composition-api').ExtractPropTypes<typeof propTypes>} props
   */
  setup(props) {
    const activeMediaStore = useActiveMediaStore()
    const activeAudio = useActiveAudio()

    const status = ref('paused')
    const currentTime = ref(0)
    const audioDuration = ref(null)

    const setPlaying = () => {
      status.value = 'playing'
      updateTimeLoop()
    }
    const setPaused = () => (status.value = 'paused')
    const setPlayed = () => (status.value = 'played')
    /**
     * @param {Event} event
     */
    const setTimeWhenPaused = (event) => {
      if (status.value !== 'playing' && event.target) {
        currentTime.value =
          /** @type {HTMLAudioElement} */ (event.target).currentTime ?? 0
        if (status.value === 'played') {
          // Set to pause to remove replay icon
          status.value = 'paused'
        }
      }
    }
    const setDuration = () => {
      audioDuration.value = activeAudio.obj.value?.duration
    }

    const updateTimeLoop = () => {
      if (activeAudio.obj.value && status.value === 'playing') {
        currentTime.value = activeAudio.obj.value.currentTime
        window.requestAnimationFrame(updateTimeLoop)
      }
    }

    watch(
      activeAudio.obj,
      (audio, _, onInvalidate) => {
        if (!audio) return
        audio.addEventListener('play', setPlaying)
        audio.addEventListener('pause', setPaused)
        audio.addEventListener('ended', setPlayed)
        audio.addEventListener('timeupdate', setTimeWhenPaused)
        audio.addEventListener('durationchange', setDuration)
        currentTime.value = audio.currentTime
        audioDuration.value = audio.duration

        /**
         * By the time the `activeAudio` is updated and a rerender
         * happens (triggering this watch function), all the events
         * we've registered above will already have fired, so we
         * need to derive the current status of the audio from the
         * `paused` and `ended` booleans on the audio object.
         *
         * In practice this will always result in the status being
         * set to `playing` as the active audio is only updated when
         * a new track is set to play. But for good measure we might
         * as well do this robustly and make sure that the status is
         * always synced any time the active audio hanges.
         */
        if (audio.paused) {
          if (audio.ended) {
            setPlayed()
          } else {
            setPaused()
          }
        } else {
          setPlaying()
        }

        onInvalidate(() => {
          audio.removeEventListener('play', setPlaying)
          audio.removeEventListener('pause', setPaused)
          audio.removeEventListener('ended', setPlayed)
          audio.removeEventListener('timeupdate', setTimeWhenPaused)
          audio.removeEventListener('durationchange', setDuration)
        })
      },
      { immediate: true }
    )

    const play = () => activeAudio.obj.value?.play()
    const pause = () => activeAudio.obj.value?.pause()

    /* Timekeeping */

    const duration = computed(
      () => audioDuration.value ?? props.audio?.duration / 1e3 ?? 0
    ) // seconds

    const message = computed(() => activeMediaStore.message)

    /* Interface with VPlayPause */

    /**
     * @param {'playing' | 'paused'} [state]
     */
    const handleToggle = (state) => {
      if (!state) {
        switch (status.value) {
          case 'playing':
            state = 'paused'
            break
          case 'paused':
          case 'played':
            state = 'playing'
            break
        }
      }

      switch (state) {
        case 'playing':
          play()
          break
        case 'paused':
          pause()
          break
      }
    }

    /* Interface with VWaveform */

    /**
     * @param {number} frac
     */
    const handleSeeked = (frac) => {
      if (activeAudio.obj.value) {
        activeAudio.obj.value.currentTime = frac * duration.value
      }
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
      message,
      handleToggle,
      handleSeeked,

      currentTime,
      duration,

      layoutComponent,
    }
  },
})
</script>
