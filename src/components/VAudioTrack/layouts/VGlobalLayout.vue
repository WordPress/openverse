<template>
  <div class="global-track flex flex-row w-full">
    <div class="flex-shrink-0">
      <AudioThumbnail :audio="audio" />
      <slot name="play-pause" size="medium" />
    </div>

    <div class="relative flex-grow">
      <div
        class="absolute inset-x-0 z-10 top-4 px-4 flex flex-row items-center justify-between"
      >
        <p class="text-sr font-semibold">{{ audio.title }}</p>
      </div>

      <slot name="controller" :waveform-props="{ 'usable-frac': 0.5 }" />
    </div>
  </div>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import AudioThumbnail from '~/components/AudioThumbnail/AudioThumbnail.vue'

export default defineComponent({
  name: 'VGlobalLayout',
  components: {
    AudioThumbnail,
  },
  props: ['audio'],
})
</script>

<style>
.global-track .thumbnail {
  @apply h-14 w-14;
}

.global-track .audio-controller {
  @apply absolute inset-0;
}

.global-track .waveform {
  @apply h-full;
}
</style>
