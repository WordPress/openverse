<template>
  <button
    type="button"
    class="play-pause flex-shrink-0 flex items-center justify-center bg-dark-charcoal text-white transition-shadow duration-100 ease-linear disabled:opacity-70 focus:outline-none focus-visible:ring focus-visible:ring-offset-2 focus-visible:ring-pink"
    @click="handleClick"
  >
    <span class="sr-only">{{ label }}</span>
    <svg
      class="h-8 w-8"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <use :href="`${icon}#icon`" />
    </svg>
  </button>
</template>

<script>
import playIcon from '~/assets/icons/play.svg'
import pauseIcon from '~/assets/icons/pause.svg'
import replayIcon from '~/assets/icons/replay.svg'

/**
 * @param {'playing' | 'paused' | 'played'} status
 */
const getLabelFromStatus = (status) => {
  switch (status) {
    case 'playing':
      return 'play-pause.pause'
    case 'paused':
      return 'play-pause.play'
    case 'played':
      return 'play-pause.replay'
  }
}

const STATUS_TO_ICON = {
  playing: pauseIcon,
  paused: playIcon,
  played: replayIcon,
}

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
      validator: (val) => ['playing', 'paused', 'played'].includes(val),
    },
  },
  computed: {
    isPlaying() {
      return this.status === 'playing'
    },
    label() {
      return this.$t(getLabelFromStatus(this.status))
    },
    icon() {
      return STATUS_TO_ICON[this.status]
    },
  },
  methods: {
    handleClick() {
      this.$emit('toggle', this.isPlaying ? 'paused' : 'playing')
    },
  },
}
</script>
