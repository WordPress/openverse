<template>
  <div class="full-track w-full">
    <div class="border-gray-3 relative border-b">
      <span
        v-if="currentTime > 0"
        class="bg-yellow-3 pointer-events-none absolute left-0 hidden h-full w-4 md:block lg:w-10"
        aria-hidden
      />
      <span
        v-if="status === 'played'"
        class="bg-yellow-3 pointer-events-none absolute right-0 hidden h-full w-4 md:block lg:w-10"
        aria-hidden
      />
      <div class="md:mx-4 lg:mx-10">
        <slot name="controller" :features="audioFeatures" :usable-frac="0.8" />
      </div>
    </div>
    <div
      class="mx-auto grid grid-cols-1 grid-rows-[auto,1fr] gap-y-6 p-6 pb-0 sm:grid-cols-[1fr,auto] sm:grid-rows-1 sm:gap-x-6 lg:mb-6 lg:max-w-5xl"
    >
      <div
        class="row-start-1 flex justify-between gap-x-6 sm:col-start-2 sm:mt-1"
      >
        <slot name="audio-control" layout="full" size="medium" />
        <VGetMediaButton
          :media="audio"
          media-type="audio"
          class="col-start-2 !w-full px-0 sm:!w-auto sm:flex-shrink-0"
        />
      </div>
      <VMediaInfo :media="audio" class="min-w-0" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import { audioFeatures, AudioSize, AudioStatus } from "~/constants/audio"

import VGetMediaButton from "~/components/VMediaInfo/VGetMediaButton.vue"
import VMediaInfo from "~/components/VMediaInfo/VMediaInfo.vue"

export default defineComponent({
  name: "VFullLayout",
  components: { VMediaInfo, VGetMediaButton },
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
  setup() {
    return {
      audioFeatures,
    }
  },
})
</script>

<style>
.full-track .waveform {
  @apply h-[185px] rounded-sm;
  --waveform-background-color: theme("colors.white");
}

.full-track .audio-control {
  @apply rounded-sm;
}
</style>
