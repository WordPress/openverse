<template>
  <div class="full-track w-full">
    <div class="relative border-b border-dark-charcoal-20">
      <span
        v-if="currentTime > 0"
        class="pointer-events-none absolute left-0 hidden h-full w-4 bg-yellow md:block lg:w-10"
        aria-hidden
      />
      <span
        v-if="status === 'played'"
        class="pointer-events-none absolute right-0 hidden h-full w-4 bg-yellow md:block lg:w-10"
        aria-hidden
      />
      <div class="md:mx-4 lg:mx-10">
        <slot name="controller" :features="[]" :usable-frac="0.8" />
      </div>
    </div>
    <slot name="audio-control" layout="full" size="medium" />
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import { AudioSize, AudioStatus } from "~/constants/audio"

export default defineComponent({
  name: "VFullLayout",
  components: {},
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
    size: {
      type: String as PropType<AudioSize>,
    },
    status: {
      type: String as PropType<AudioStatus>,
    },
    currentTime: {
      type: Number,
      required: true,
    },
  },
})
</script>
