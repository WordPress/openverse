<template>
  <div class="full-track w-full">
    <div class="bg-dark-charcoal-06 relative">
      <span
        v-if="currentTime > 0"
        class="pointer-events-none absolute h-full hidden md:block w-4 lg:w-10 left-0 bg-yellow"
        aria-hidden
      />
      <span
        v-if="status === 'played'"
        class="pointer-events-none absolute h-full hidden md:block w-4 lg:w-10 right-0 bg-yellow"
        aria-hidden
      />
      <div class="md:mx-4 lg:mx-10">
        <slot name="controller" :features="audioFeatures" :usable-frac="0.8" />
      </div>
    </div>
    <div
      class="flex flex-row flex-wrap lg:flex-nowrap items-top px-4 lg:px-0 lg:max-w-5xl mx-auto gap-6 mt-6"
    >
      <slot name="play-pause" :size="isSmall ? 'small' : 'medium'" />

      <div
        class="audio-info order-2 lg:order-1 w-full lg:w-auto flex flex-col justify-center"
      >
        <h1
          class="text-base lg:text-3xl font-heading font-semibold lg:line-clamp-2"
        >
          {{ audio.title }}
        </h1>
        <div
          class="subtitle mt-1 flex flex-col lg:flex-row lg:items-center gap-2"
        >
          <i18n
            as="span"
            path="audio-track.creator"
            class="font-semibold leading-snug"
          >
            <template #creator>
              <VLink
                class="p-px rounded-sm focus:outline-none focus:ring focus:ring-pink"
                :href="audio.creator_url"
              >
                {{ audio.creator }}
              </VLink>
            </template>
          </i18n>

          <span class="hidden lg:block text-dark-charcoal-70">{{
            $t('interpunct')
          }}</span>

          <div>{{ timeFmt(audio.duration || 0) }}</div>
        </div>
      </div>

      <VButton
        as="VLink"
        :href="audio.foreign_landing_url"
        :size="isSmall ? 'small' : 'medium'"
        class="ms-auto order-1 lg:order-2 font-bold"
      >
        {{ $t('download-button.download') }}
      </VButton>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { AudioDetail } from '~/models/media'
import { AudioSize, AudioStatus, audioFeatures } from '~/constants/audio'

import VButton from '~/components/VButton.vue'
import VLink from '~/components/VLink.vue'

export default defineComponent({
  name: 'VFullLayout',
  components: { VButton, VLink },
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
  setup(props) {
    /**
     * Format the time as hh:mm:ss, dropping the hour part if it is zero.
     * @param ms - the number of milliseconds in the duration
     * @returns the duration in a human-friendly format
     */
    const timeFmt = (ms: number): string => {
      if (ms) {
        const date = new Date(0)
        date.setSeconds(ms / 1e3)
        return date.toISOString().substr(11, 8).replace(/^00:/, '')
      }
      return '--:--'
    }

    const isSmall = computed(() => props.size === 's')

    return {
      timeFmt,

      isSmall,
      audioFeatures,
    }
  },
})
</script>

<style>
.full-track .waveform {
  @apply h-[185px] rounded-sm;
}

.full-track .play-pause {
  @apply rounded-sm;
}
</style>
