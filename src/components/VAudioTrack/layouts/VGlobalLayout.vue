<template>
  <div class="global-track flex flex-row w-full">
    <div class="flex-shrink-0">
      <VAudioThumbnail :audio="audio" />
      <slot name="play-pause" size="medium" />
    </div>

    <div class="relative flex-grow">
      <VLink
        :href="`/audio/${audio.id}`"
        class="absolute inset-x-0 z-10 top-[10.5px] px-4 flex flex-row items-center justify-between line-clamp-2 pe-12 text-sr font-semibold"
      >
        {{ audio.title }}
      </VLink>

      <slot name="controller" :usable-frac="0.5" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from '@nuxtjs/composition-api'

import type { AudioDetail } from '~/models/media'

import VAudioThumbnail from '~/components/VAudioThumbnail/VAudioThumbnail.vue'
import VLink from '~/components/VLink.vue'

export default defineComponent({
  name: 'VGlobalLayout',
  components: {
    VAudioThumbnail,
    VLink,
  },
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
  },
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
