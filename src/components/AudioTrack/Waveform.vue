<template>
  <div
    ref="el"
    class="waveform relative bg-dark-charcoal-04 overflow-x-hidden"
    tabIndex="0"
    role="slider"
    :aria-label="$t('waveform.label')"
    aria-orientation="horizontal"
    aria-valuemin="0"
    :aria-valuemax="duration"
    :aria-valuenow="currentTime"
    :aria-valuetext="currentTimeText"
    @mousedown="handleMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
    @mouseleave="handleMouseLeave"
    @keydown.arrow-left="handleArrows"
    @keydown.arrow-right="handleArrows"
  >
    <svg
      class="w-full h-full"
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
      <rect
        v-for="(peak, index) in normalizedPeaks"
        :key="index"
        class="transform origin-bottom transition-transform duration-500"
        :class="[
          isReady ? 'scale-y-100' : 'scale-y-0',
          spaceBefore(index) < seekBarWidth
            ? 'fill-black'
            : 'fill-dark-charcoal-20',
        ]"
        :x="spaceBefore(index)"
        :y="spaceAbove(peak)"
        :width="barWidth"
        :height="peak"
      />
    </svg>

    <!-- Timestamps -->
    <template v-if="isReady">
      <div
        ref="progressTimestampEl"
        class="progress timestamp z-10 bg-yellow transform"
        :class="[
          ...(isProgressTimestampCutoff
            ? ['bg-dark-charcoal-04-opaque']
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
      <div
        v-if="showDuration"
        class="duration timestamp right-0 bg-dark-charcoal-04-opaque"
      >
        {{ timeFmt(duration) }}
      </div>
    </template>

    <!-- Loading overlay -->
    <div
      v-else
      class="absolute inset-x-0 inset-y-0 flex items-center justify-center loading font-bold text-sm"
    >
      {{ $t('waveform.loading') }}
    </div>
  </div>
</template>

<script>
import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
} from '@nuxtjs/composition-api'
import { downsampleArray, upsampleArray } from '~/utils/resampling.js'

/**
 * Renders an SVG representation of the waveform given a list of heights for the
 * bars.
 */
export default {
  name: 'Waveform',
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
     * whether the audio metadata has been loaded and is ready to display
     */
    isReady: {
      type: Boolean,
      default: false,
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
     * whether to show the duration of the audio at the ending edge
     */
    showDuration: {
      type: Boolean,
      default: false,
    },
  },
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
      return xPos / waveformWidth.value
    }

    /* Element dimensions */

    const el = ref(null) // template ref
    const waveformWidth = ref(0)
    const updateWaveformWidth = () => {
      waveformWidth.value = el.value.clientWidth
    }
    const observer = new ResizeObserver(updateWaveformWidth)
    onMounted(() => {
      observer.observe(el.value)
      updateWaveformWidth()
    })
    onBeforeUnmount(() => {
      observer.disconnect()
    })

    /* Resampling */

    const barWidth = 2
    const barGap = 2
    const peakCount = computed(() => {
      const count = (waveformWidth.value - barGap) / (barWidth + barGap)
      return Math.floor(count)
    })
    const normalizedPeaks = computed(() => {
      const givenLength = props.peaks.length
      const required = peakCount.value
      if (givenLength < required) {
        return upsampleArray(props.peaks, required)
      } else if (givenLength > required) {
        return downsampleArray(props.peaks, required)
      }
      return props.peaks
    })

    /* SVG drawing */

    /**
     * the fraction of space to reserve for the timestamps above the bars; The
     * `viewBox` height of the waveform will be 1 + `timestampSpace`.
     */
    const timestampSpace = 0.33 // % of bar height
    const viewBoxHeight = 1 + timestampSpace
    const viewBox = computed(
      () => `0 0 ${waveformWidth.value} ${viewBoxHeight}`
    )
    const spaceBefore = (index) => index * barWidth + (index + 1) * barGap
    const spaceAbove = (peak) => viewBoxHeight - peak

    /* Progress bar */

    const currentFrac = computed(() =>
      props.isReady ? props.currentTime / props.duration : 0
    )
    const progressBarWidth = computed(() => {
      const frac = isDragging.value ? seekFrac.value : currentFrac.value
      return waveformWidth.value * frac
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
      return waveformWidth.value * frac
    })

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
      return props.isReady ? seekDelta / props.duration : 0
    })
    const modSeekDeltaFrac = computed(() =>
      props.isReady ? modSeekDelta / props.duration : 0
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

    const handleArrows = (event) => {
      clearSeekProgress()
      const { key, shiftKey } = event
      const magnitude = shiftKey ? modSeekDeltaFrac.value : seekDeltaFrac.value
      const direction = key.includes('Left') ? -1 : 1
      const delta = magnitude * direction
      emit('seeked', currentFrac.value + delta)
    }

    return {
      timeFmt,

      el, // template ref

      barWidth,
      normalizedPeaks,

      viewBox,
      spaceBefore,
      spaceAbove,

      progressBarWidth,
      progressTimestamp,
      progressTimestampEl,
      isProgressTimestampCutoff,

      seekFrac,
      seekBarWidth,
      seekTimestamp,
      seekTimestampEl,
      isSeekTimestampCutoff,

      handleMouseDown,
      handleMouseMove,
      handleMouseUp,
      handleMouseLeave,

      handleArrows,
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
}
</script>

<style scoped lang="css">
.timestamp {
  @apply absolute top-1 font-bold text-sm px-1 pointer-events-none;
}

.progress {
  left: var(--progress-time-left);
}

.seek {
  left: var(--seek-time-left);
}

.bg-dark-charcoal-04-opaque {
  /* opaque equivalent of dark-charcoal-04 on top of white */
  background-color: rgb(247, 246, 247);
}
</style>
