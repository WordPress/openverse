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
import {
  computed,
  defineComponent,
  ref,
  useStore,
  onMounted,
  watch,
} from '@nuxtjs/composition-api'

import VPlayPause from '~/components/VAudioTrack/VPlayPause.vue'
import VWaveform from '~/components/VAudioTrack/VWaveform.vue'

import VFullLayout from '~/components/VAudioTrack/layouts/VFullLayout.vue'
import VRowLayout from '~/components/VAudioTrack/layouts/VRowLayout.vue'
import VBoxLayout from '~/components/VAudioTrack/layouts/VBoxLayout.vue'
import VGlobalLayout from '~/components/VAudioTrack/layouts/VGlobalLayout.vue'

import { ACTIVE } from '~/constants/store-modules'
import {
  PAUSE_ACTIVE_MEDIA_ITEM,
  SET_ACTIVE_MEDIA_ITEM,
} from '~/constants/mutation-types'

/**
 * Displays the waveform and basic information about the track, along with
 * controls to play, pause or seek to a point on the track.
 */
export default defineComponent({
  name: 'VAudioTrack',
  components: {
    VPlayPause,
    VWaveform,

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
    const store = useStore()

    /* Local status */

    const status = ref('paused')
    /**
     * Set the local status to 'playing' and start measuring the current time.
     */
    const localPlay = () => {
      status.value = 'playing'
      updateTimeLoop()
    }
    /**
     * Set the local status to 'paused'.
     */
    const localPause = () => {
      status.value = 'paused'
    }
    onMounted(() => {
      if (isActiveTrack.value && store.state.active.status === 'playing') {
        localPlay()
      } else {
        localPause()
      }
    })

    /* Timekeeping */

    const currentTime = ref(0) // seconds
    const duration = computed(() => (props.audio.duration ?? 0) / 1e3) // seconds

    const updateTime = () => {
      if (
        window?.audioEl &&
        /**
         * When the user switches from playing one audio track to another,
         * say on the related audio section, if we don't check that the src
         * of the audio element matches the source of the audio for this
         * current instance of the audio track component, then we'll end up
         * updating this instances `currentTime` ref to the value of the
         * current time of the audio playing for the other element.
         *
         * The effect of this is that when you're switching audio tracks that
         * are playing, the previous track that was playing will end up having
         * it's current time set to the current time of the next audio track.
         */
        window.audioEl.src === props.audio.url
      ) {
        currentTime.value = window.audioEl.currentTime
        if (currentTime.value >= duration.value) {
          store.commit(`${ACTIVE}/${PAUSE_ACTIVE_MEDIA_ITEM}`)
          status.value = 'played'
        }
      }
    }

    const updateTimeLoop = () => {
      updateTime()
      if (status.value === 'playing') {
        // Audio is playing, keep looping
        window.requestAnimationFrame(updateTimeLoop)
      } else {
        // Update time one last time on the next frame to try to fix
        // some weird, difficult to reproduce, seemingly machine
        // dependent bugs, described in the PR discussion below:
        // https://github.com/WordPress/openverse-frontend/pull/633
        window.requestAnimationFrame(updateTime)
      }
    }

    /* Interface with active media store */

    const isActiveTrack = computed(
      () =>
        store.state.active.type === 'audio' &&
        store.state.active.id === props.audio.id
    )
    const message = computed(() => store.state.active.message)

    /**
     * Plays the audio using the `HTMLAudioElement`.
     */
    const elPlay = () => {
      if (window?.audioEl) {
        if (window.audioEl.src !== props.audio.url) {
          window.audioEl.src = props.audio.url
          // Set the current time of the audio back to the seeked time
          // of the waveform/timeline. In the future we might change
          // this to reset the audio back to 0 anytime another audio
          // is played but for now this is simpler and requires less
          // cross-instance communication.
          window.audioEl.currentTime = currentTime.value
        }
        window.audioEl.play()
      }
    }
    /**
     * Pauses the audio using the `HTMLAudioElement` and updates local state.
     */
    const elPause = () => {
      if (window?.audioEl) {
        window.audioEl.pause()
      }
    }
    watch(
      () => [store.state.active.id, store.state.active.status],
      ([activeId, activeStatus], [prevActiveId, prevActiveStatus]) => {
        if (activeStatus === 'ejected') {
          elPause()
          localPause()
        } else if (activeStatus !== prevActiveStatus && isActiveTrack.value) {
          // Track status changed
          switch (activeStatus) {
            case 'playing':
              elPlay()
              localPlay()
              break
            case 'paused':
              elPause()
              localPause()
              break
          }
        } else if (activeId !== prevActiveId) {
          // Track ID changed
          if (isActiveTrack.value) {
            elPlay()
            localPlay()
          } else {
            localPause()
          }
        } else {
          // Nothing changed, no action required
        }
      }
    )

    /* Interface with VPlayPause */

    /**
     * Changes the store state to 'playing' with the information about the
     * track. This invokes the active media state watcher which, in turn, calls
     * `elPlay` to actually play the audio.
     */
    const storePlay = () => {
      store.commit(`${ACTIVE}/${SET_ACTIVE_MEDIA_ITEM}`, {
        type: 'audio',
        id: props.audio.id,
      })
    }
    /**
     * Changes the store state to 'paused'. If this is the active track, this
     * invokes the active media state watcher which, in turn, calls `elPause` to
     * actually pause the audio.
     */
    const storePause = () => {
      store.commit(`${ACTIVE}/${PAUSE_ACTIVE_MEDIA_ITEM}`)
    }
    const handleToggle = (state) => {
      switch (state) {
        case 'playing':
          storePlay()
          break
        case 'paused':
          if (isActiveTrack.value) {
            storePause()
          }
          break
      }
    }

    /* Interface with VWaveform */

    /**
     * Always update the current time ref when seeking happens
     * for this audio track so that seeking can happen on one
     * track even if it's not being played, and then that new
     * time will get used if this instance's track gets played.
     *
     * Otherwise seeking will appear to not work on paused
     * audio tracks.
     *
     * @param {number} frac
     */
    const elSetTime = (frac) => {
      const seekedTime = frac * (props.audio.duration / 1e3)
      currentTime.value = seekedTime
      if (window?.audioEl && isActiveTrack.value) {
        window.audioEl.currentTime = seekedTime
      }
    }
    const handleSeeked = (frac) => {
      elSetTime(frac)
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
