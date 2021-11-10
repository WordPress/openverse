<template>
  <button
    type="button"
    class="play-pause flex-shrink-0 flex items-center justify-center bg-dark-charcoal text-white transition-shadow duration-100 ease-linear disabled:opacity-70 focus:outline-none focus-visible:ring focus-visible:ring-offset-2 focus-visible:ring-pink"
    @click="handleClick"
  >
    <span class="sr-only">{{ $t(label) }}</span>
    <VIcon :icon-path="icon" />
  </button>
</template>

<script>
import VIcon from '~/components/VIcon/VIcon.vue'

import playIcon from '~/assets/icons/play.svg'
import pauseIcon from '~/assets/icons/pause.svg'
import replayIcon from '~/assets/icons/replay.svg'

/**
 * Displays the control for switching between the playing and paused states of
 * a media file.
 */
export default {
  name: 'PlayPause',
  components: { VIcon },
  model: {
    prop: 'status',
    event: 'toggle',
  },
  props: {
    /**
     * the current play status of the audio
     */
    status: {
      type: String,
      validator: (val) => ['playing', 'paused', 'played'].includes(val),
    },
  },
  data() {
    return {
      statusVerbMap: {
        playing: 'pause',
        paused: 'play',
        played: 'replay',
      },
      statusIconMap: {
        playing: pauseIcon,
        paused: playIcon,
        played: replayIcon,
      },
    }
  },
  computed: {
    isPlaying() {
      return this.status === 'playing'
    },
    /**
     * Get the button label based on the current status of the player.
     */
    label() {
      return `play-pause.${this.statusVerbMap[this.status]}`
    },
    /**
     * Get the button icon based on the current status of the player.
     */
    icon() {
      return this.statusIconMap[this.status]
    },
  },
  methods: {
    handleClick() {
      this.$emit('toggle', this.isPlaying ? 'paused' : 'playing')
    },
  },
}
</script>
