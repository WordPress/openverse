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
      class="mx-auto grid grid-cols-1 grid-rows-[auto,auto] gap-6 p-6 pb-0 lg:mb-6 lg:max-w-5xl"
    >
      <div class="row-start-1 flex justify-between gap-x-6 sm:col-start-2">
        <slot name="play-pause" size="medium" />
        <VButton
          as="VLink"
          :href="audio.foreign_landing_url"
          size="large"
          variant="filled-pink"
          has-icon-end
          show-external-icon
          :external-icon-size="6"
          class="description-bold col-start-2 flex-shrink-0"
          :send-external-link-click-event="false"
          @click="sendGetMediaEvent"
        >
          {{ $t("audioDetails.weblink") }}
        </VButton>
      </div>

      <div
        class="audio-info row-start-2 flex w-full flex-col justify-center sm:col-start-1 sm:row-start-1 lg:w-auto"
      >
        <h1 class="description-bold lg:heading-5 lg:line-clamp-2">
          {{ audio.title }}
        </h1>
        <div
          class="subtitle mt-1 flex flex-col gap-2 text-base leading-snug lg:flex-row lg:items-center"
        >
          <i18n as="span" path="audioTrack.creator" class="font-semibold">
            <template #creator>
              <VLink
                class="rounded-sm p-px focus-visible:outline-none focus-visible:ring focus-visible:ring-pink"
                :href="audio.creator_url"
                :send-external-link-click-event="false"
              >
                {{ audio.creator }}
              </VLink>
            </template>
          </i18n>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import { timeFmt } from "~/utils/time-fmt"
import { AudioStatus, audioFeatures } from "~/constants/audio"
import { AUDIO } from "~/constants/media"
import { useAnalytics } from "~/composables/use-analytics"
import { useUiStore } from "~/stores/ui"

import VButton from "~/components/VButton.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VFullLayout",
  components: { VButton, VLink },
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
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
    const uiStore = useUiStore()

    const isSm = computed(() => uiStore.isBreakpoint("sm"))

    const { sendCustomEvent } = useAnalytics()

    const sendGetMediaEvent = () => {
      sendCustomEvent("GET_MEDIA", {
        id: props.audio.id,
        provider: props.audio.provider,
        mediaType: AUDIO,
      })
    }

    return {
      isSm,
      timeFmt,

      audioFeatures,

      sendGetMediaEvent,
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
