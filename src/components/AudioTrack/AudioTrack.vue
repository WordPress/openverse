<template>
  <div
    class="audio-track"
    :aria-label="$t('audio-track.aria-label')"
    role="region"
  >
    <!-- Only visible in compact player -->
    <div v-if="isCompact" class="info-section flex justify-between">
      <i18n path="audio-track.title" tag="p">
        <template #title>
          <NuxtLink to="#" class="text-pink hover:text-pink hover:underline">
            {{ audio.title }}</NuxtLink
          >
        </template>
        <template #creator>{{ audio.creator }}</template>
      </i18n>
      {{ audio.category }}
    </div>

    <div class="interactive-section flex flex-row gap-2">
      <PlayPause
        v-if="isCompact"
        class="flex-shrink-0"
        :is-playing="isPlaying"
        :disabled="!isReady"
        @toggle="setPlayerState"
      />
      <div
        class="flex-grow"
        @keypress.enter="setPlayerState(!isPlaying)"
        @keypress.space="setPlayerState(!isPlaying)"
      >
        <Waveform
          :class="isCompact ? 'h-20' : 'h-30'"
          :message="message ? $t(`audio-track.messages.${message}`) : null"
          :current-time="currentTime"
          :duration="duration"
          :peaks="audio.peaks"
          :show-duration="isCompact"
          @seeked="setPosition"
        />
      </div>
    </div>

    <!-- Only visible in expanded player -->
    <div v-if="!isCompact" class="info-section flex flex-row gap-6">
      <PlayPause
        :aria-controls="audio.id"
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
      :id="audio.id"
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
      @error="handleError"
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
    /**
     * whether to render the player in a compact style; This places the waveform
     * and the play-pause button on the same line.
     */
    isCompact: {
      type: Boolean,
      default: false,
    },
  },
  data: () => ({
    player: null, // HTMLAudioElement
    currentTime: 0,
    duration: 0,
    message: 'loading',
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

    isReady() {
      return this.message === null
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
      this.message = null
    },
    setIsPlaying(isPlaying) {
      this.isPlaying = isPlaying
    },
    handleError(event) {
      const error = event.target.error
      switch (error.code) {
        case error.MEDIA_ERR_ABORTED:
          this.message = 'err_aborted'
          break
        case error.MEDIA_ERR_NETWORK:
          this.message = 'err_network'
          break
        case error.MEDIA_ERR_DECODE:
          this.message = 'err_decode'
          break
        case error.MEDIA_ERR_SRC_NOT_SUPPORTED:
          this.message = 'err_unsupported'
          break
      }
    },
  },
}
</script>
