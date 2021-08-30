<template>
  <button
    type="button"
    class="flex items-center justify-center bg-dark-charcoal h-20 w-20 transition-shadow duration-100 ease-linear disabled:opacity-70 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-pink"
    @click="toggle"
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
  props: {
    /**
     * whether the media associated with the button is currently playing
     */
    isPlaying: {
      type: Boolean,
    },
  },
  data: () => ({
    icons: {
      play: playIcon,
      pause: pauseIcon,
    },
  }),
  computed: {
    label() {
      return this.$t(this.isPlaying ? 'play-pause.pause' : 'play-pause.play')
    },
  },
  methods: {
    toggle() {
      this.$emit('toggle', !this.isPlaying)
    },
  },
}
</script>
