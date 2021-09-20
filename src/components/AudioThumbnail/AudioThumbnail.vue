<template>
  <!-- Should be wrapped by a fixed-width parent -->
  <div class="relative h-0 w-full pt-full" :title="helpText">
    <div class="absolute inset-0 bg-yellow">
      <img
        v-if="audio.thumbnail"
        class="h-full w-full object-cover object-center overflow-clip"
        :src="audio.thumbnail"
        :alt="helpText"
      />
    </div>
  </div>
</template>

<script>
/**
 * Displays the cover art for the audio in a square aspect ratio.
 */
export default {
  name: 'AudioThumbnail',
  props: {
    /**
     * the details of the audio whose artwork is to be shown; The properties
     * `thumbnail`, `title` and `creator` are used.
     */
    audio: {
      type: Object,
      required: true,
    },
  },
  computed: {
    helpText() {
      return this.$t('audio-thumbnail.alt', {
        title: this.audio.title,
        creator: this.audio.creator,
      })
    },
  },
}
</script>
