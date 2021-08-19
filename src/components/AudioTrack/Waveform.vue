<template>
  <div
    ref="waveform"
    class="waveform relative bg-dark-charcoal-04 overflow-x-hidden"
  >
    <svg
      class="w-full h-full"
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="viewBox"
      preserveAspectRatio="none"
      @mousemove="setSeekProgress"
      @mouseleave="clearSeekProgress"
      @click="seek"
    >
      <rect
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

    <div
      v-if="!isReady"
      class="absolute inset-x-0 inset-y-0 flex items-center justify-center loading font-bold text-sm"
    >
      {{ $t('waveform.loading') }}
    </div>
    <div
      class="current absolute top-1 font-bold text-sm bg-yellow z-10 px-1 transform -translate-x-full pointer-events-none"
      :style="{ '--current-time-left': `${progressBarWidth}px` }"
    >
      {{ timeFmt(currentTime) }}
    </div>
    <div
      v-if="seekPercentage"
      class="seek absolute top-1 font-bold text-sm px-1 transform -translate-x-full pointer-events-none"
      :style="{ '--seek-time-left': `${seekBarWidth}px` }"
    >
      {{ timeFmt(seekPercentage * duration) }}
    </div>
    <div
      v-if="showDuration"
      class="duration absolute top-1 right-0 px-1 font-bold text-sm pointer-events-none"
    >
      {{ timeFmt(duration) }}
    </div>
  </div>
</template>

<script>
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
  data: () => ({
    barWidth: 2, // px
    barGap: 2, // px
    timestampSpace: 0.33, // % of bar height

    /**
     * the position of the graph that the user is hovering over to seek
     */
    seekPercentage: null,

    waveformWidth: 100, // dummy start value
    observer: null, // ResizeObserver
  }),
  computed: {
    percentage() {
      return this.isReady ? this.currentTime / this.duration : 0
    },

    peakCount() {
      return Math.floor(
        (this.waveformWidth - this.barGap) / (this.barWidth + this.barGap)
      )
    },
    normalizedPeaks() {
      if (this.peaks.length < this.peakCount) {
        return upsampleArray(this.peaks, this.peakCount)
      } else if (this.peaks.length > this.peakCount) {
        return downsampleArray(this.peaks, this.peakCount)
      }
      return this.peaks
    },

    viewBoxHeight() {
      return 1 + this.timestampSpace
    },
    viewBox() {
      return `0 0 ${this.waveformWidth} ${this.viewBoxHeight}`
    },

    progressBarWidth() {
      return this.waveformWidth * this.percentage
    },
    seekBarWidth() {
      return this.waveformWidth * (this.seekPercentage ?? this.percentage)
    },
  },
  async mounted() {
    this.updateWaveformWidth()
    this.observer = new ResizeObserver(this.updateWaveformWidth)
    this.observer.observe(this.$el)
  },
  beforeDestroy() {
    this.observer.disconnect()
  },
  methods: {
    /**
     * Format the time as hh:mm:ss, dropping the hour part if it is zero.
     * @returns {string} the duration in a human-friendly format
     */
    timeFmt(seconds) {
      const date = new Date(0)
      date.setSeconds(seconds)
      return date.toISOString().substr(11, 8).replace(/^00:/, '')
    },

    spaceBefore(index = this.peakCount) {
      return index * this.barWidth + (index + 1) * this.barGap
    },
    spaceAbove(peak) {
      return this.viewBoxHeight - peak
    },

    updateWaveformWidth() {
      this.waveformWidth = this.$el.clientWidth
    },

    // Event handlers
    getPositionPercentage(event) {
      const x = event.clientX - this.$el.getBoundingClientRect().x
      return x / this.waveformWidth
    },
    setSeekProgress(event) {
      this.seekPercentage = this.getPositionPercentage(event)
    },
    clearSeekProgress() {
      this.seekPercentage = null
    },
    seek(event) {
      this.$emit('seeked', this.getPositionPercentage(event))
    },
  },
}
</script>

<style scoped lang="css">
.current {
  left: var(--current-time-left);
}

.seek {
  left: var(--seek-time-left);
}

.duration {
  /* opaque equivalent of dark-charcoal-04 on top of white */
  background-color: rgb(247, 246, 247);
}
</style>
