<template>
  <div ref="waveform" class="waveform bg-dark-charcoal-04" @click="setProgress">
    <svg
      class="w-full h-full"
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="viewBox"
      preserveAspectRatio="none"
      @click="seek"
    >
      <rect
        class="fill-yellow"
        x="0"
        y="0"
        :width="progressBarWidth"
        height="1"
      />
      <rect
        v-for="(peak, index) in normalizedPeaks"
        :key="index"
        class="transform origin-bottom"
        :class="[
          spaceBefore(index) < progressBarWidth
            ? 'fill-black'
            : 'fill-dark-charcoal-20',
        ]"
        :x="spaceBefore(index)"
        :y="spaceAbove(peak)"
        :width="barWidth"
        :height="peak"
      />
    </svg>
  </div>
</template>

<script>
import { upsampleArray, downsampleArray } from '~/utils/resampling.js'

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
  },
  data: () => ({
    barWidth: 2, // px
    barGap: 2, // px

    /**
     * the percentage of the graph that has been played; This represents the
     * seekbar of the audio player. A number from 1-100.
     */
    percentage: 0,

    waveformWidth: 100, // dummy start value
    observer: null, // ResizeObserver
  }),
  computed: {
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

    viewBox() {
      return `0 0 ${this.waveformWidth} 1`
    },
    progressBarWidth() {
      return this.waveformWidth * this.percentage
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
    spaceBefore(index = this.peakCount) {
      return index * this.barWidth + (index + 1) * this.barGap
    },
    spaceAbove(peak) {
      return 1 - peak
    },
    updateWaveformWidth() {
      this.waveformWidth = this.$el.clientWidth
    },
    setProgress(event) {
      const startPosition = this.$refs.waveform.getBoundingClientRect().left
      const newPosition = event.clientX
      this.percentage = (newPosition - startPosition) / this.waveformWidth
    },
  },
}
</script>
