<template>
  <div class="global-track flex w-full flex-row">
    <div class="flex-shrink-0">
      <VAudioThumbnail :audio="audio" />
      <slot name="play-pause" size="medium" layout="global" />
    </div>

    <div class="relative flex-grow overflow-hidden bg-white">
      <div class="flex h-12 items-center justify-between">
        <VLink
          :href="`/audio/${audio.id}`"
          class="hover-underline label-bold z-10 flex flex-row items-center px-3 pe-12 text-dark-charcoal"
          :class="{ 'blur-text': shouldBlur }"
        >
          {{ shouldBlur ? $t("sensitiveContent.title.audio") : audio.title }}
        </VLink>
      </div>
      <div class="h-12"><slot name="controller" :usable-frac="1" /></div>
    </div>
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
  @apply h-12 w-12;
}

.global-track .waveform {
  @apply h-full;
}
</style>
