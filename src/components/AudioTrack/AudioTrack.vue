<template>
  <div class="audio-track" aria-label="Audio Player" role="region">
    <div class="waveform-section bg-dark-charcoal-04">
      <Waveform
        class="h-30 w-full"
        :is-ready="isReady"
        :current-time="currentTime"
        :duration="duration"
        :peaks="audio.peaks"
        @seeked="setPosition"
        @jumpSeekedForward="jumpPositionForward"
        @jumpSeekedBackward="jumpPositionBackward"
      />
    </div>
    <div class="info-section flex flex-row gap-6">
      <PlayPause
        :aria-controls="ariaIdentifier"
        class="self-start flex-shrink-0"
        :is-playing="isPlaying"
        :disabled="!isReady"
        @toggle="setPlayerState"
      />
      <div class="info self-end">
        <i18n path="audio-track.title" tag="p">
          <template #title>
            <strong>{{ audio.title }}</strong>
          </template>
          <template #creator>
            <a
              class="text-pink hover:text-pink hover:underline"
              :href="audio.creatorUrl"
              >{{ audio.creator }}</a
            >
          </template>
        </i18n>
        <p class="-mt-2">
          {{ durationFmt }}
        </p>
      </div>
    </div>

    <!-- eslint-disable vuejs-accessibility/media-has-caption -->
    <audio
      v-show="false"
      :id="ariaIdentifier"
      ref="audio"
      controls
      :src="audio.url"
      crossorigin="anonymous"
      @loadedmetadata="
        setIsReady()
        updateTime()
      "
      @play="setIsPlaying(true)"
      @pause="setIsPlaying(false)"
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
    player: null, // HTMLAudioElement
    currentTime: 0,
    duration: 0,
    /** Amount in seconds to jump seek **/
    seekJumpDuration: 15,

    isReady: false,
    isPlaying: false,
  }),
  computed: {
    /**
     * Get the duration of the song in hh:mm:ss format, dropping the hour part
     * if it is zero.
     * @returns {string} the duration in a human-friendly format
     */
    durationFmt() {
      const seconds = (this.audio.duration ?? 0) / 1e3 // ms -> s
      const date = new Date(0)
      date.setSeconds(seconds)
      return date.toISOString().substr(11, 8).replace(/^00:/, '')
    },
    /**
     * A unique string to represent the audio player in aria properties
     * @returns {string} the id of the audio file prefixed with 'audio-'
     */
    ariaIdentifier() {
      return `audio-${this.audio.id}`
    },
  },
  mounted() {
    this.player = this.$refs.audio
  },
  methods: {
    updateTime() {
      this.currentTime = this.player.currentTime
      this.duration = this.player.duration
    },
    syncTime() {
      if (this.player) {
        this.updateTime()
      }
      if (this.isPlaying) {
        // still playing, keep looping
        window.requestAnimationFrame(this.syncTime)
      }
    },

    // Subcomponent events
    setPosition(percentage) {
      if (this.player.duration) {
        this.player.currentTime = this.player.duration * percentage
        this.updateTime()
      }
    },
    jumpPositionForward() {
      this.player.currentTime = this.player.currentTime + this.seekJumpDuration
      this.updateTime()
    },
    jumpPositionBackward() {
      this.player.currentTime = this.player.currentTime - this.seekJumpDuration
      this.updateTime()
    },
    async setPlayerState(isPlaying) {
      if (isPlaying) {
        await this.player.play()
        window.requestAnimationFrame(this.syncTime)
      } else {
        await this.player.pause()
      }
    },

    // HTMLAudioElement events
    setIsReady() {
      this.isReady = true
    },
    setIsPlaying(isPlaying) {
      this.isPlaying = isPlaying
    },
  },
}
</script>
