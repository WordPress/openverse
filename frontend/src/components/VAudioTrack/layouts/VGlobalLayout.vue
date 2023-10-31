<template>
  <div
    class="global-track grid w-full grid-cols-[3rem,1fr] grid-rows-[3rem,3rem] rounded"
  >
    <div class="h-12 w-12 rounded-ss"><VAudioThumbnail :audio="audio" /></div>

    <div class="flex h-12 items-center justify-between rounded-se bg-white">
      <VLink
        :href="`/audio/${audio.id}`"
        class="hover-underline label-bold z-10 flex flex-row items-center px-3 pe-12 text-dark-charcoal"
        :class="{ 'blur-text': shouldBlur }"
      >
        {{ shouldBlur ? $t("sensitiveContent.title.audio") : audio.title }}
      </VLink>
    </div>
    <slot name="audio-control" size="medium" layout="global" />
    <slot name="controller" :usable-frac="1" />
  </div>
</template>

<script lang="ts">
import { toRefs, defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"

import { useSensitiveMedia } from "~/composables/use-sensitive-media"

import VAudioThumbnail from "~/components/VAudioThumbnail/VAudioThumbnail.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VGlobalLayout",
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
  setup(props) {
    const { audio } = toRefs(props)
    const { isHidden: shouldBlur } = useSensitiveMedia(audio)

    return {
      shouldBlur,
    }
  },
})
</script>

<style>
.global-track .thumbnail {
  @apply h-12 w-12 rounded-ss;
}
.global-track .thumbnail img {
  @apply rounded-ss;
}

.global-track .waveform {
  @apply h-full rounded-ee;
}
.global-track .audio-control {
  @apply rounded-es;
}
</style>
