<template>
  <div class="full-track w-full">
    <slot name="controller" />

    <div class="flex flex-row space-between mx-16 my-6">
      <div class="left-content flex flex-row items-center gap-6">
        <slot name="play-pause" />

        <div class="audio-info">
          <i18n
            tag="h1"
            class="text-3xl font-heading font-semibold"
            path="audio-track.title"
          >
            <template #title>{{ audio.title }}</template>
            <template #creator>
              <a class="text-pink hover:text-pink" :href="audio.creator_url">{{
                audio.creator
              }}</a>
            </template>
          </i18n>
          <p class="text-base leading-snug mt-1">
            {{ timeFmt(audio.duration) }}
          </p>
        </div>
      </div>

      <!-- TODO: Download dropdown -->
      <div class="right-content bg-pink h-12 w-30 rounded-sm ml-auto" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'Full',
  props: ['audio'],
  setup() {
    /**
     * Format the time as hh:mm:ss, dropping the hour part if it is zero.
     * @param {number} ms - the number of milliseconds in the duration
     * @returns {string} the duration in a human-friendly format
     */
    const timeFmt = (ms) => {
      const date = new Date(0)
      date.setSeconds(ms / 1e3)
      return date.toISOString().substr(11, 8).replace(/^00:/, '')
    }

    return {
      timeFmt,
    }
  },
}
</script>

<style>
.full-track .waveform {
  @apply h-30 rounded-sm;
}

.full-track .play-pause {
  @apply h-14 w-14 rounded-sm;
}
</style>
