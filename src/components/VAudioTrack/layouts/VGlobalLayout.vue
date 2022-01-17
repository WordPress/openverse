<template>
  <div class="global-track flex flex-row w-full">
    <div class="flex-shrink-0">
      <VAudioThumbnail :audio="audio" />
      <slot name="play-pause" size="medium" />
    </div>

    <div class="relative flex-grow">
      <div
        class="absolute inset-x-0 z-10 top-4 px-4 flex flex-row items-center justify-between"
      >
        <p class="text-sr font-semibold">{{ audio.title }}</p>
      </div>

      <slot name="controller" :usable-frac="0.5" />
    </div>
  </div>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import VAudioThumbnail from '~/components/VAudioThumbnail/VAudioThumbnail.vue'

export default defineComponent({
  name: 'VGlobalLayout',
  components: {
    VAudioThumbnail,
  },
  props: ['audio'],
})
</script>

<style>
.global-track .thumbnail {
  @apply h-14 w-14;
}

.global-track .waveform {
  @apply h-full;
}
</style>
