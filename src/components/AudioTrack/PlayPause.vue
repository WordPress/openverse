<template>
  <button
    type="button"
    class="play-pause flex items-center justify-center bg-dark-charcoal transition-shadow duration-100 ease-linear disabled:opacity-70 focus:outline-none focus-visible:ring focus-visible:ring-offset-2 focus-visible:ring-pink"
    @click="handleClick"
  >
    <span class="sr-only">{{ label }}</span>
    <svg
      class="text-white h-8 w-8"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <use v-if="isPlaying" :href="`${icons.pause}#icon`" />
      <use v-else :href="`${icons.play}#icon`" />
    </svg>
  </button>
</template>

<script>
import playIcon from '~/assets/icons/play.svg'
import pauseIcon from '~/assets/icons/pause.svg'

/**
 * Displays the control for switching between the playing and paused states of
 * a media file.
 */
export default {
  name: 'PlayPause',
  model: {
    prop: 'status',
    event: 'toggle',
  },
  props: {
    /**
     * the playing/paused status of the audio
     */
    status: {
      type: String,
      validator: (val) => ['playing', 'paused'].includes(val),
    },
  },
  data: () => ({
    icons: {
      play: playIcon,
      pause: pauseIcon,
    },
  }),
  computed: {
    isPlaying() {
      return this.status === 'playing'
    },
    label() {
      return this.$t(this.isPlaying ? 'play-pause.pause' : 'play-pause.play')
    },
  },
  methods: {
    handleClick() {
      this.$emit('toggle', this.isPlaying ? 'paused' : 'playing')
    },
  },
}
</script>
