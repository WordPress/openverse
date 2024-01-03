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
      v-if="additionalSearchViews"
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
    <div
      v-else
      class="mx-auto grid grid-cols-1 grid-rows-[auto,auto] gap-6 p-6 pb-0 lg:mb-6 lg:max-w-5xl lg:flex-nowrap"
    >
      <div class="row-start-1 flex justify-between gap-x-6 sm:col-start-2">
        <slot name="audio-control" layout="full" size="medium" />
        <VGetMediaButton
          :media="audio"
          media-type="audio"
          class="col-start-2 !w-full px-0 sm:!w-auto sm:flex-shrink-0"
        />
      </div>

      <div
        class="audio-info row-start-2 flex w-full flex-col justify-center sm:col-start-1 sm:row-start-1 lg:w-auto"
      >
        <h1 class="heading-6 lg:line-clamp-2">{{ audio.title }}</h1>
        <div
          class="subtitle mt-1 flex flex-col gap-2 text-base leading-snug lg:flex-row lg:items-center"
        >
          <i18n-t as="span" keypath="audioTrack.creator" class="font-semibold" tag="span">
            <template #creator>
              <VLink
                class="rounded-sm p-px focus-visible:outline-none focus-visible:ring focus-visible:ring-pink"
                :href="audio.creator_url"
                :send-external-link-click-event="false"
              >
                {{ audio.creator }}
              </VLink>
            </template>
          </i18n-t>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import { timeFmt } from "~/utils/time-fmt"
import { audioFeatures, AudioSize, AudioStatus } from "~/constants/audio"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useProviderStore } from "~/stores/provider"

import VLink from "~/components/VLink.vue"
import VGetMediaButton from "~/components/VMediaInfo/VGetMediaButton.vue"
import VMediaInfo from "~/components/VMediaInfo/VMediaInfo.vue"

export default defineComponent({
  name: "VFullLayout",
  components: { VMediaInfo, VGetMediaButton, VLink },
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

    const featureFlagStore = useFeatureFlagStore()
    const additionalSearchViews = computed(() =>
      featureFlagStore.isOn("additional_search_views")
    )

    const providerStore = useProviderStore()
    const sourceName = computed(() => {
      return providerStore.getProviderName(
        props.audio.source ?? props.audio.provider,
        "audio"
      )
    })

    return {
      timeFmt,

      isSmall,
      audioFeatures,
      sourceName,

      additionalSearchViews,
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
