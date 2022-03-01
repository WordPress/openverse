<template>
  <div
    ref="el"
    class="waveform group relative bg-background-var focus:outline-none overflow-hidden"
    :style="{
      '--usable-height': `${Math.floor(usableFrac * 100)}%`,
      '--unusable-height': `${Math.floor((1 - usableFrac) * 100)}%`,
    }"
    :tabIndex="isInteractive ? 0 : -1"
    :role="isInteractive ? 'slider' : null"
    :aria-disabled="!isInteractive"
    :aria-label="$t('waveform.label')"
    aria-orientation="horizontal"
    aria-valuemin="0"
    :aria-valuemax="duration"
    :aria-valuenow="currentTime"
    :aria-valuetext="currentTimeText"
    v-on="eventHandlers"
  >
    <!-- Focus ring -->
    <svg
      v-if="isInteractive"
      class="hidden group-focus:block absolute inset-0 w-full h-full z-20 shadow-ring-1"
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="viewBox"
      preserveAspectRatio="none"
    >
      <!-- Stroke is calculated from the centre of the path -->
      <rect
        v-if="waveformDimens.width && waveformDimens.height"
        class="stroke-pink"
        x="0.75"
        y="0.75"
        :width="waveformDimens.width - 1.5"
        :height="waveformDimens.height - 1.5"
        rx="2"
        fill="none"
        stroke-width="1.5"
      />
      <rect
        v-if="waveformDimens.width && waveformDimens.height"
        class="stroke-white"
        x="2"
        y="2"
        :width="waveformDimens.width - 4"
        :height="waveformDimens.height - 4"
        fill="none"
        stroke-width="1"
        rx="0.75"
      />
    </svg>

    <!-- Progress bar -->
    <svg
      class="absolute inset-0 w-full h-full"
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="viewBox"
      preserveAspectRatio="none"
    >
      <rect
        v-if="isReady"
        class="fill-yellow"
        x="0"
        y="0"
        :width="progressBarWidth"
        height="100%"
      />
    </svg>

    <!-- Bars -->
    <svg
      class="bars absolute bottom-0 w-full"
      :class="{ 'with-space': showDuration || showTimestamps }"
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="viewBox"
      preserveAspectRatio="none"
    >
      <rect
        v-for="(peak, index) in normalizedPeaks"
        :key="index"
        class="transform origin-bottom transition-transform duration-500"
        :class="[
          isReady ? 'scale-y-100' : 'scale-y-0',
          index <= seekIndex ? 'fill-black' : 'fill-dark-charcoal-20-alpha',
        ]"
        :x="spaceBefore(index)"
        :y="spaceAbove(index)"
        :width="barWidth"
        :height="peak"
      />
    </svg>

    <!-- Focus bar -->
    <div
      v-if="isInteractive"
      class="focus-indicator hidden absolute z-30 top-0 flex flex-col items-center justify-between bg-black h-full"
      :style="{ width: `${barWidth}px`, left: `${progressBarWidth}px` }"
    >
      <div
        v-for="(classes, name) in {
          top: ['-translate-y-1/2'],
          bottom: ['translate-y-1/2'],
        }"
        :key="name"
        class="rounded-full bg-black h-2 w-2 transform"
        :class="classes"
      >
        &nbsp;
      </div>
    </div>

    <!-- Timestamps -->
    <template v-if="isReady">
      <template v-if="showTimestamps">
        <div
          ref="progressTimestampEl"
          class="progress timestamp z-10 transform"
          :class="[
            ...(isProgressTimestampCutoff
              ? ['bg-background-var']
              : ['bg-yellow', '-translate-x-full']),
          ]"
          :style="{ '--progress-time-left': `${progressBarWidth}px` }"
        >
          {{ timeFmt(progressTimestamp) }}
        </div>
        <div
          v-if="seekFrac"
          ref="seekTimestampEl"
          class="seek timestamp transform"
          :class="{ '-translate-x-full': !isSeekTimestampCutoff }"
          :style="{ '--seek-time-left': `${seekBarWidth}px` }"
        >
          {{ timeFmt(seekTimestamp) }}
        </div>
      </template>
      <div
        v-if="showDuration"
        class="duration timestamp right-0 bg-background-var"
      >
        {{ timeFmt(duration) }}
      </div>
    </template>

    <!-- Message overlay -->
    <div
      v-else
      class="absolute inset-0 flex items-center justify-center loading font-bold text-xs"
    >
      {{ message }}
    </div>

    <!-- Seek disabled message overlay -->
    <div
      v-if="seekDisabledNotice"
      class="invisible group-hover:visible group-focus:visible absolute w-full inset-0 flex items-center justify-center font-bold text-xsm bg-yellow/75 z-40"
    >
      {{ seekDisabledNotice }}
    </div>
  </div>
</template>

<script>
import {
  computed,
  defineComponent,
  onBeforeUnmount,
  onMounted,
  ref,
} from '@nuxtjs/composition-api'

import { downsampleArray, upsampleArray } from '~/utils/resampling'
import * as keycodes from '~/utils/key-codes'

/**
 * Renders an SVG representation of the waveform given a list of heights for the
 * bars.
 */
export default defineComponent({
  name: 'VWaveform',
  props: {
    /**
     * an array of heights of the bars; The waveform will be generated with
     * bars of random length if the prop is not provided.
     */
    peaks: {
      type: Array,
      required: false,
      default: () => Array.from({ length: 100 }, () => Math.random()),
      validator: (val) => val.every((item) => item >= 0 && item <= 1),
    },
    /**
     * the message to display instead of the waveform; This is useful when
     * displaying a loading or error state.
     */
    message: {
      type: String,
    },
    /**
     * the current play time of the audio track
     */
    currentTime: {
      type: Number,
      default: 0,
    },
    /**
     * the total play time of the audio track
     */
    duration: {
      type: Number,
      default: 0,
    },
    /**
     * the fraction of the waveform height to use for the bars and timestamp;
     * The remaining space can be used to place other elements.
     */
    usableFrac: {
      type: Number,
      default: 1,
    },
    /**
     * selectively enable features in the waveform; Available features are
     * `'timestamp'`, `'duration'`, `'seek'`.
     */
    features: {
      type: Array,
      default: () => ['timestamps', 'seek'],
    },
    /**
     * An object of notices to display when a feature is disabled.
     * `'timestamp'`, `'duration'`, `'seek'`.
     */
    featureNotices: {
      type: Object,
      default: () => ({}),
    },
  },
  emits: [
    /**
     * Emitted when the waveform receives mouse events for seeking,
     * either single clicks on a specific part of the waveform,
     * or a click and drag.
     *
     * Also emitted when the waveform receives arrow key or home/end
     * keyboard events that also correspond to seeking.
     */
    'seeked',
  ],
  setup(props, { emit }) {
    /* Utils */

    /**
     * Format the time as hh:mm:ss, dropping the hour part if it is zero.
     * @param {number} seconds - the number of seconds in the duration
     * @returns {string} the duration in a human-friendly format
     */
    const timeFmt = (seconds) => {
      const date = new Date(0)
      date.setSeconds(seconds)
      return date.toISOString().substr(11, 8).replace(/^00:/, '')
    }
    /**
     * Get the x-coordinate of the event with respect to the bounding box of the
     * waveform.
     * @param {MouseEvent} event - the event from which to get the position
     * @returns {number} the x-position of the event inside the waveform
     */
    const getPosition = (event) => {
      return event.clientX - el.value.getBoundingClientRect().x
    }
    /**
     * Get the x-position of the event with respect to the bounding box of the
     * waveform, as a fraction of the waveform width.
     * @param {MouseEvent} event - the event from which to get the position
     * @returns {number} the x-position of the event as a fraction
     */
    const getPositionFrac = (event) => {
      const xPos = getPosition(event)
      return xPos / waveformDimens.value.width
    }
    /**
     * Get the number of peaks that will fit within the given width.
     * @param {number} width - the number of pixels inside which to count peaks
     * @returns {number} the number of peaks that can be accommodated
     */
    const getPeaksInWidth = (width) => {
      return Math.floor((width - barGap) / (barWidth + barGap))
    }

    /* Element dimensions */

    const el = ref(null) // template ref
    const waveformDimens = ref({ width: 0, height: 0 })
    const updateWaveformDimens = () => {
      waveformDimens.value = {
        width: el.value.clientWidth,
        height: el.value.clientHeight,
      }
    }
    let observer
    onMounted(() => {
      if (window.ResizeObserver) {
        observer = new ResizeObserver(updateWaveformDimens)
        observer.observe(el.value)
      }
      updateWaveformDimens()
    })
    onBeforeUnmount(() => {
      if (observer) {
        observer.disconnect()
      }
    })

    /* Features */

    const showDuration = computed(() => props.features.includes('duration'))
    const showTimestamps = computed(() => props.features.includes('timestamps'))
    const isSeekable = computed(() => props.features.includes('seek'))

    /* Feature notices */
    const seekDisabledNotice = computed(() => props.featureNotices?.seek)

    /* State */

    const isReady = computed(() => !props.message)
    const isInteractive = computed(() => isSeekable.value && isReady.value)

    /* Resampling */

    const barWidth = 2
    const barGap = 2
    const peakCount = computed(() =>
      getPeaksInWidth(waveformDimens.value.width)
    )
    const normalizedPeaks = computed(() => {
      let samples = props.peaks

      const givenLength = samples.length
      const required = peakCount.value
      if (givenLength < required) {
        samples = upsampleArray(samples, required)
      } else if (givenLength > required) {
        samples = downsampleArray(samples, required)
      }

      return samples.map((peak) => peak * waveformDimens.value.height)
    })

    /* SVG drawing */

    const viewBox = computed(() =>
      [0, 0, waveformDimens.value.width, waveformDimens.value.height].join(' ')
    )
    const spaceBefore = (index) => index * barWidth + index * barGap
    const spaceAbove = (index) =>
      waveformDimens.value.height - normalizedPeaks.value[index]

    /* Progress bar */

    const currentFrac = computed(() =>
      isReady.value ? props.currentTime / props.duration : 0
    )
    const progressBarWidth = computed(() => {
      const frac = isDragging.value ? seekFrac.value : currentFrac.value
      return waveformDimens.value.width * frac
    })

    /* Progress timestamp */

    const progressTimestampEl = ref(null)
    const progressTimestamp = computed(() =>
      isDragging.value ? seekTimestamp.value : props.currentTime
    )
    const isProgressTimestampCutoff = computed(() => {
      if (!progressTimestampEl.value) return false
      const barWidth = progressBarWidth.value
      const timestampWidth = progressTimestampEl.value.offsetWidth
      return barWidth < timestampWidth + 2
    })

    /* Seek bar */

    const seekFrac = ref(null)
    const seekBarWidth = computed(() => {
      const frac = seekFrac.value ?? currentFrac.value
      return waveformDimens.value.width * frac
    })
    const seekIndex = computed(() => getPeaksInWidth(seekBarWidth.value))

    /* Seek timestamp */

    const seekTimestampEl = ref(null)
    const seekTimestamp = computed(() => seekFrac.value * props.duration)
    const isSeekTimestampCutoff = computed(() => {
      if (!seekTimestampEl.value) return false
      const barWidth = seekBarWidth.value
      const timestampWidth = seekTimestampEl.value.offsetWidth
      return barWidth < timestampWidth + 2
    })

    /* Seeking */

    const seekDelta = 1 // s
    const modSeekDelta = 15 // s
    /**
     * the seek jump length as a % of the track
     */
    const seekDeltaFrac = computed(() => {
      return isReady.value ? seekDelta / props.duration : 0
    })
    const modSeekDeltaFrac = computed(() =>
      isReady.value ? modSeekDelta / props.duration : 0
    )
    const setSeekProgress = (event) => {
      seekFrac.value = getPositionFrac(event)
    }
    const clearSeekProgress = () => {
      seekFrac.value = null
    }
    const seek = (event) => {
      emit('seeked', getPositionFrac(event))
    }

    /* Dragging */

    const dragThreshold = 2 // px
    let startPos = null
    const isDragging = ref(false)
    const handleMouseDown = (event) => {
      isDragging.value = false
      startPos = getPosition(event)
      setSeekProgress(event)
    }
    const handleMouseMove = (event) => {
      if (startPos) {
        const clickPos = getPosition(event)
        if (Math.abs(clickPos - startPos) > dragThreshold) {
          isDragging.value = true
        }
      }
      setSeekProgress(event)
    }
    const handleMouseUp = (event) => {
      isDragging.value = false
      startPos = null
      seek(event)
    }
    const handleMouseLeave = () => {
      clearSeekProgress()
    }

    /* Keyboard */

    const handlePosKeys = (frac) => {
      clearSeekProgress()
      emit('seeked', frac)
    }
    const handleArrowKeys = (event) => {
      const { key, shiftKey, metaKey } = event
      if (metaKey) {
        // Always false on Windows
        handlePosKeys(key.includes('Left') ? 0 : 1)
      } else {
        clearSeekProgress()
        const direction = key.includes('Left') ? -1 : 1
        const magnitude = shiftKey
          ? modSeekDeltaFrac.value
          : seekDeltaFrac.value
        const delta = magnitude * direction
        emit('seeked', currentFrac.value + delta)
      }
    }

    const handleSpacebar = () => {
      emit('toggle-playback')
    }

    /**
     * @param {KeyboardEvent} event
     */
    const willBeHandled = (event) =>
      [
        keycodes.ArrowLeft,
        keycodes.ArrowRight,
        keycodes.Home,
        keycodes.End,
        keycodes.Spacebar,
      ].includes(event.key)

    /**
     * @param {KeyboardEvent} event
     */
    const handleKeys = (event) => {
      if (!willBeHandled(event)) return

      event.preventDefault()
      if ([keycodes.ArrowLeft, keycodes.ArrowRight].includes(event.key))
        return handleArrowKeys(event)
      if (event.key === keycodes.Home) return handlePosKeys(0)
      if (event.key === keycodes.End) return handlePosKeys(1)
      if (event.key === keycodes.Spacebar) return handleSpacebar()
    }

    /* v-on */

    const eventHandlers = computed(() => {
      if (isInteractive.value) {
        return {
          mousedown: handleMouseDown,
          mousemove: handleMouseMove,
          mouseup: handleMouseUp,
          mouseleave: handleMouseLeave,
          keydown: handleKeys,
        }
      } else {
        return {}
      }
    })

    return {
      timeFmt,

      el, // template ref

      showDuration,
      showTimestamps,
      isSeekable,

      seekDisabledNotice,

      isReady,
      isInteractive,

      barWidth,
      normalizedPeaks,

      waveformDimens,
      viewBox,
      spaceBefore,
      spaceAbove,

      progressBarWidth,
      progressTimestamp,
      progressTimestampEl,
      isProgressTimestampCutoff,

      seekFrac,
      seekBarWidth,
      seekIndex,

      seekTimestamp,
      seekTimestampEl,
      isSeekTimestampCutoff,

      handleMouseDown,
      handleMouseMove,
      handleMouseUp,
      handleMouseLeave,

      handlePosKeys,
      handleArrowKeys,

      eventHandlers,
    }
  },
  computed: {
    /**
     * the waveform current time as a text string; This function was placed
     * outside because `this` is not accessible inside the `setup`.
     */
    currentTimeText() {
      const time = this.timeFmt(this.currentTime)
      return this.$t('waveform.current-time', { time })
    },
  },
})
</script>

<style scoped lang="css">
.waveform {
  --v-background-color: var(
    --waveform-background-color,
    theme('colors.dark-charcoal.06')
  );
}

.timestamp {
  @apply absolute font-bold text-xs px-1 pointer-events-none;
  top: calc(var(--unusable-height) + theme('spacing[0.5]'));
}

.bg-background-var {
  background-color: var(--v-background-color);
}

.bars {
  height: calc(var(--usable-height));
}

.bars.with-space {
  height: calc(var(--usable-height) - 1rem - 2 * theme('spacing[0.5]'));
}

.progress {
  left: var(--progress-time-left);
}

.seek {
  left: var(--seek-time-left);
}

.waveform:focus-visible .focus-indicator {
  display: flex;
}

.fill-dark-charcoal-20-alpha {
  fill: rgba(48, 39, 46, 0.2);
}
</style>
