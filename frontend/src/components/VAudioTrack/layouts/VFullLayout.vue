<script setup lang="ts">
import { audioFeatures, AudioSize, AudioStatus } from "#shared/constants/audio"
import type { AudioDetail } from "#shared/types/media"

import VGetMediaButton from "~/components/VMediaInfo/VGetMediaButton.vue"
import VMediaInfo from "~/components/VMediaInfo/VMediaInfo.vue"

defineProps<{
  audio: AudioDetail
  size?: AudioSize
  status?: AudioStatus
  currentTime: number
}>()
</script>

<template>
  <div class="full-track w-full">
    <div class="relative border-b border-default">
      <span
        v-if="currentTime > 0"
        class="pointer-events-none absolute left-0 hidden h-full w-4 bg-complementary md:block lg:w-10"
        aria-hidden
      />
      <span
        v-if="status === 'played'"
        class="pointer-events-none absolute right-0 hidden h-full w-4 bg-complementary md:block lg:w-10"
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
        <slot
          name="audio-control"
          v-bind="{ layout: 'full', size: 'medium' } as const"
        />
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

<style>
.full-track .waveform {
  @apply h-[185px] rounded-sm;
  --waveform-background-color: theme("backgroundColor.default");
}

.full-track .audio-control {
  @apply rounded-sm;
}
</style>
