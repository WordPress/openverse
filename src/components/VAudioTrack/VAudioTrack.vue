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
  watch,
  onUnmounted,
  useRoute,
} from '@nuxtjs/composition-api'

import { useActiveAudio } from '~/composables/use-active-audio'

import VPlayPause from '~/components/VAudioTrack/VPlayPause.vue'
import VWaveform from '~/components/VAudioTrack/VWaveform.vue'

import VFullLayout from '~/components/VAudioTrack/layouts/VFullLayout.vue'
import VRowLayout from '~/components/VAudioTrack/layouts/VRowLayout.vue'
import VBoxLayout from '~/components/VAudioTrack/layouts/VBoxLayout.vue'
import VGlobalLayout from '~/components/VAudioTrack/layouts/VGlobalLayout.vue'

import { ACTIVE, MEDIA } from '~/constants/store-modules'
import {
  PAUSE_ACTIVE_MEDIA_ITEM,
  SET_ACTIVE_MEDIA_ITEM,
} from '~/constants/mutation-types'

const propTypes = {
  /**
   * the information about the track, typically from a track's detail endpoint
   */
  audio: {
    type: /** @type {import('@nuxtjs/composition-api').PropType<import('~/store/types').AudioDetail>} */ (
      Object
    ),
    required: /** @type {true} */ (true),
  },
  /**
   * the arrangement of the contents on the canvas; This determines the
   * overall L&F of the audio component.
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
  props: propTypes,
  /**
   * @param {import('@nuxtjs/composition-api').ExtractPropTypes<typeof propTypes>} props
   */
  setup(props) {
    const store = useStore()
    const route = useRoute()

    const activeAudio = useActiveAudio()

    const status = ref('paused')
    const currentTime = ref(0)

    const initLocalAudio = () => {
      // Preserve existing local audio if we plucked it from the global active audio
      if (!localAudio) localAudio = new Audio(props.audio.url)

      localAudio.addEventListener('play', setPlaying)
      localAudio.addEventListener('pause', setPaused)
      localAudio.addEventListener('ended', setPlayed)
      localAudio.addEventListener('timeupdate', setTimeWhenPaused)

      /**
       * Similar to the behavior in the global audio track,
       * if the local audio was set to an already existing and
       * matching active global track, then we'll need to initialize
       * the status based on the `paused` and `ended` booleans
       * on the audio object.
       *
       * For newly initialized audio objects, this is harmless,
       * but it is essential for making sure page transitions
       * preserve the existing, already manipulated audio
       * object's state.
       *
       * Unlike the global audio track, however, this will not
       * always result in a status of `playing` in practice,
       * as the state of the active global track could be any
       * of the three statuses we track when the page transition
       * happens. For example, the audio track on the result page
       * could have been played through (and thus `ended`), or it
       * could be paused mid-way (and thus `paused`), or neither
       * and thus would be playing.
       */
      if (localAudio.paused) {
        if (localAudio.ended) {
          setPlayed()
        } else {
          setPaused()
        }
      } else {
        setPlaying()
      }

      currentTime.value = localAudio.currentTime
    }

    /**
     * We can only create the local audio object on the client,
     * so the initialization of this variable is hidden inside
     * the `initLocalAudio` function which is only called when
     * playback is first requested or when the track if first seeked.
     *
     * However, when navigating to an audio result page, if
     * the globally active audio already matches the result
     * that was clicked on, hijack that object instead and
     * treat it as the local audio for this instance.
     *
     * @type {HTMLAudioElement | undefined}
     * */
    let localAudio =
      activeAudio.obj.value?.src === props.audio.url
        ? activeAudio.obj.value
        : undefined

    const updateTimeLoop = () => {
      if (localAudio && status.value === 'playing') {
        currentTime.value = localAudio.currentTime
        window.requestAnimationFrame(updateTimeLoop)
      }
    }

    const setPlaying = () => {
      status.value = 'playing'
      activeAudio.obj.value = localAudio
      store.commit(`${ACTIVE}/${SET_ACTIVE_MEDIA_ITEM}`, {
        type: 'audio',
        id: props.audio.id,
      })
      updateTimeLoop()
    }
    const setPaused = () => {
      status.value = 'paused'
      store.commit(`${ACTIVE}/${PAUSE_ACTIVE_MEDIA_ITEM}`)
    }
    const setPlayed = () => (status.value = 'played')
    const setTimeWhenPaused = () => {
      if (status.value !== 'playing' && localAudio) {
        currentTime.value = localAudio.currentTime
        if (status.value === 'played') {
          // Set to pause to remove replay icon
          status.value = 'paused'
        }
      }
    }

    /**
     * If we're transforming the globally active audio
     * into our local audio, then we need to initialize
     * the local state syncing from the audio object
     * to our local refs.
     *
     * This lives here instead of closer to where `localAudio`
     * is defined because `initLocalAudio` and several of
     * the functions it depends on also all depend on the
     * `localAudio` variable. This is the earliest in
     * `setup` that this can be called.
     */
    if (localAudio) initLocalAudio()

    onUnmounted(() => {
      if (!localAudio) return

      localAudio.removeEventListener('play', setPlaying)
      localAudio.removeEventListener('pause', setPaused)
      localAudio.removeEventListener('ended', setPlayed)
      localAudio.removeEventListener('timeupdate', setTimeWhenPaused)

      if (
        route.value.params.id == props.audio.id ||
        store.getters[`${MEDIA}/results`]?.items?.[props.audio.id]
      ) {
        /**
         * If switching to any route other than the single result
         * route for this track, pause it. Otherwise, let it keep
         * playing to introduce a "seamless" feeling beween the
         * search results page and the single result page.
         *
         * This handles going from the search page to the single
         * result page for a different track than is currently playing.
         * It also handles the same interaction for related audio.
         * Also for related audio, it will handle pausing any related
         * audio when navigating back from the single result page
         * to the search results page.
         *
         * Also, if the currently playing audio is present in the
         * existing list of search results, then also let it keep
         * playing.
         */
        return
      }

      localAudio.pause()
    })

    const play = () => {
      // delay initializing the local audio element until playback is requested
      if (!localAudio) initLocalAudio()
      localAudio?.play()
    }
    const pause = () => localAudio?.pause()

    watch(
      activeAudio.obj,
      (audio) => {
        if (audio !== localAudio && status.value === 'playing') {
          localAudio?.pause()
        }
      },
      { immediate: true }
    )

    /* Timekeeping */

    const duration = computed(() => (props.audio?.duration ?? 0) / 1e3) // seconds

    const message = computed(() => store.state.active.message)

    /* Interface with VPlayPause */

    /**
     * @param {'playing' | 'paused'} state
     */
    const handleToggle = (state) => {
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
      if (!localAudio) initLocalAudio()
      /**
       * Calling initLocalAudio will guarantee localAudio
       * to be an HTMLAudioElement, but we can't prove that
       * to TypeScript without jumping through some tricky
       * hoops (using `assert`) or adding unnecessary
       * runtime checks.
       */
      // @ts-ignore
      localAudio.currentTime = frac * duration.value
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
