<template>
  <div class="full-track w-full">
    <div class="relative bg-dark-charcoal-06">
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
        <slot name="controller" :features="audioFeatures" :usable-frac="0.8" />
      </div>
    </div>
    <div
      class="items-top mx-auto mt-6 flex flex-row flex-wrap gap-6 px-6 lg:max-w-5xl lg:flex-nowrap"
    >
      <slot name="play-pause" :size="isSmall ? 'small' : 'medium'" />

      <div
        class="audio-info order-2 flex w-full flex-col justify-center lg:order-1 lg:w-auto"
      >
        <h1
          class="font-heading text-base font-semibold leading-[1.3] lg:text-3xl lg:line-clamp-2"
        >
          {{ audio.title }}
        </h1>
        <div
          class="subtitle mt-1 flex flex-col gap-2 text-base leading-[1.3] lg:flex-row lg:items-center"
        >
          <i18n as="span" path="audio-track.creator" class="font-semibold">
            <template #creator>
              <VLink
                class="rounded-sm p-px focus:outline-none focus:ring focus:ring-pink"
                :href="audio.creator_url"
              >
                {{ audio.creator }}
              </VLink>
            </template>
          </i18n>

          <span class="hidden text-dark-charcoal-70 lg:block">{{
            $t('interpunct')
          }}</span>

          <div>{{ timeFmt(audio.duration || 0) }}</div>
        </div>
      </div>

      <VButton
        as="VLink"
        :href="audio.foreign_landing_url"
        size="disabled"
        class="order-1 px-6 py-3 text-sr font-semibold ms-auto md:px-6 md:py-4 md:text-2xl lg:order-2"
      >
        {{ $t('audio-details.weblink') }}
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
