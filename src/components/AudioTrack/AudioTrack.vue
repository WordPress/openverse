<template>
  <div class="audio-track">
    <div class="waveform-section bg-dark-charcoal-04">
      <Waveform
        class="h-30 w-full"
        :percentage="progress"
        @sought="updateSeekbar"
      />
    </div>
    <div class="info-section flex flex-row items-end">
      <PlayPause :is-playing="isPlaying" @toggle="setPlayState" />
      <div class="info ml-6">
        <p>
          <strong>{{ audio.title }}</strong> by
          <a
            class="text-pink hover:text-pink hover:underline"
            :href="audio.creatorUrl"
            >{{ audio.creator }}</a
          >
        </p>
        <p class="-mt-2">
          {{ durationFmt }}
        </p>
      </div>
    </div>

    <!-- eslint-disable vuejs-accessibility/media-has-caption -->
    <audio
      v-show="false"
      ref="audio"
      controls
      :src="audio.url"
      crossorigin="anonymous"
    />
    <!-- eslint-enable vuejs-accessibility/media-has-caption -->
  </div>
</template>

<script>
import Waveform from '~/components/AudioTrack/Waveform.vue'
import PlayPause from '~/components/AudioTrack/PlayPause.vue'

/**
 * Displays the waveform and basic information about the track, along with
 * controls to play, pause or seek to a point on the track.
 */
export default {
  name: 'AudioTrack',
  components: { PlayPause, Waveform },
  props: {
    /**
     * the information about the track, typically from a track's detail endpoint
     */
    audio: {
      type: Object,
      required: true,
    },
  },
  data: () => ({
    progress: 0,
    player: null, // HTMLAudioElement
    isPlaying: false,
  }),
  computed: {
    /**
     * Get the duration of the song in hh:mm:ss format, dropping the hour part
     * if it is zero.
     * @returns {string} the duration in a human-friendly format
     */
    durationFmt() {
      const seconds = (this.audio.duration ?? 0) / 1000 // ms -> s
      const date = new Date(0)
      date.setSeconds(seconds)
      return date.toISOString().substr(11, 8).replace(/^00:/, '')
    },
  },
  watch: {
    isPlaying(toVal) {
      if (!toVal) {
        return // no animation when playback is paused
      }

      // smoothly animate the progressbar on the waveform component
      const loop = () => {
        this.updateProgressBar()
        if (this.isPlaying) {
          // still playing, keep looping
          window.requestAnimationFrame(loop)
        }
      }
      window.requestAnimationFrame(loop)
    },
  },
  mounted() {
    this.player = this.$refs.audio
  },
  methods: {
    updateProgressBar() {
      const elapsed = this.player.currentTime
      const total = this.player.duration
      this.progress = elapsed / total
    },
    updateSeekbar(percentage) {
      if (this.player.duration) {
        this.player.currentTime = this.player.duration * percentage
      }
      this.updateProgressBar()
    },
    setPlayState(isPlaying) {
      this.isPlaying = isPlaying
      if (this.isPlaying) {
        this.player.play()
      } else {
        this.player.pause()
      }
    },
  },
}
</script>
