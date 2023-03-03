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
        <slot name="controller" :features="audioFeatures" :usable-frac="0.8" />
      </div>
    </div>
    <div
      class="items-top mx-auto mt-6 flex flex-row flex-wrap gap-6 px-6 lg:max-w-5xl lg:flex-nowrap"
    >
      <slot name="play-pause" :size="isSmall ? 'small' : 'large'" />

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

          <span
            class="hidden text-dark-charcoal-70 lg:block"
            aria-hidden="true"
            >{{ $t("interpunct") }}</span
          >

          <div>{{ timeFmt(audio.duration || 0, true) }}</div>
        </div>
      </div>

      <VButton
        as="VLink"
        :href="audio.foreign_landing_url"
        size="disabled"
        class="order-1 self-center px-6 py-3 text-sr font-semibold ms-auto md:px-6 md:py-4 md:text-2xl lg:order-2"
      >
        {{ $t("audio-details.weblink") }}
        <VIcon
          :icon-path="externalIcon"
          :rtl-flip="true"
          :size="4"
          class="ms-2 md:h-6 md:w-6"
        />
      </VButton>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import { timeFmt } from "~/utils/time-fmt"
import { AudioSize, AudioStatus, audioFeatures } from "~/constants/audio"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VLink from "~/components/VLink.vue"

import externalIcon from "~/assets/icons/external-link.svg"

export default defineComponent({
  name: "VFullLayout",
  components: { VButton, VIcon, VLink },
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
    const isSmall = computed(() => props.size === "s")

    return {
      timeFmt,

      isSmall,
      audioFeatures,
      externalIcon,
    }
  },
})
</script>

<style>
.full-track .waveform {
  @apply h-[185px] rounded-sm;
  --waveform-background-color: theme("colors.white");
}

.full-track .play-pause {
  @apply rounded-sm;
}
</style>
