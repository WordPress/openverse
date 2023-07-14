<template>
  <!-- `pages/search/audio` has negative margin `-mx-4` to compensate for this padding. -->
  <article
    class="row-track flex flex-row p-2 hover:bg-dark-charcoal-06 md:p-4"
    :class="[`size-${size}`, { 'items-start': isSmall }]"
  >
    <div
      class="relative flex-shrink-0 overflow-hidden rounded-sm"
      :class="isLarge ? 'me-6 w-30' : 'me-4 w-20'"
    >
      <VAudioThumbnail :audio="audio" />
      <div v-show="isSmall" class="absolute bottom-0 ltr:right-0 rtl:left-0">
        <slot name="play-pause" size="tiny" layout="row" :is-tabbable="false" />
      </div>
    </div>

    <div
      class="flex-grow"
      :class="{
        'flex flex-row gap-8': isMedium,
        'flex flex-col justify-between': isLarge,
      }"
    >
      <div class="flex-shrink-0" :class="{ 'w-70': isMedium }">
        <div
          class="decoration-inherit font-heading line-clamp-2 block rounded-sm p-px font-semibold text-dark-charcoal hover:text-dark-charcoal focus:outline-none focus:ring focus:ring-pink group-hover:underline md:line-clamp-1"
          :class="{
            'text-2xl': isMedium || isLarge,
            'leading-snug': isSmall,
            'blur-text': shouldBlur,
          }"
        >
          {{ shouldBlur ? $t("sensitiveContent.title.audio") : audio.title }}
        </div>

        <div
          class="mt-2 flex text-dark-charcoal-70"
          :class="{
            'text-sr': isSmall,
            'leading-snug': isMedium || isLarge,
            'flex-col gap-2': isSmall || isMedium,
            'flex-row items-center': isLarge,
          }"
        >
          <div class="part-a">
            <i18n
              tag="span"
              path="audioTrack.creator"
              :class="{ 'blur-text': shouldBlur }"
            >
              <template #creator>{{
                shouldBlur ? $t("sensitiveContent.creator") : audio.creator
              }}</template> </i18n
            ><span v-show="isLarge" class="mx-2" aria-hidden="true">{{
              $t("interpunct")
            }}</span>
          </div>

          <div class="part-b inline-flex flex-row items-center">
            <span v-show="isSmall">
              <span
                class="inline-block rounded-sm bg-dark-charcoal-06 p-1 font-semibold text-dark-charcoal"
                >{{ timeFmt(audio.duration || 0, true) }}</span
              ><span class="mx-2" aria-hidden="true">{{
                $t("interpunct")
              }}</span>
            </span>

            <span v-if="audio.category">
              <span>{{ $t(`filters.audioCategories.${audio.category}`) }}</span
              ><span class="mx-2" aria-hidden="true">{{
                $t("interpunct")
              }}</span>
            </span>

            <VLicense :hide-name="isSmall" :license="audio.license" />
          </div>
        </div>
      </div>

      <div
        v-show="!isSmall"
        class="flex flex-row"
        :class="{
          'flex-grow': isMedium,
        }"
      >
        <slot
          name="play-pause"
          :size="isLarge ? 'large' : 'extra-large'"
          :layout="'row'"
          :is-tabbable="false"
        />
        <slot
          name="controller"
          :features="features"
          :feature-notices="featureNotices"
          :is-tabbable="false"
        />
      </div>
    </div>
  </article>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { timeFmt } from "~/utils/time-fmt"
import type { AudioDetail } from "~/types/media"
import type { AudioSize } from "~/constants/audio"
import { useUiStore } from "~/stores/ui"

import VAudioThumbnail from "~/components/VAudioThumbnail/VAudioThumbnail.vue"
import VLicense from "~/components/VLicense/VLicense.vue"

export default defineComponent({
  name: "VRowLayout",
  components: {
    VAudioThumbnail,
    VLicense,
  },
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
    size: {
      type: String as PropType<AudioSize>,
      required: false,
    },
  },
  setup(props) {
    const featureNotices: {
      timestamps?: string
      duration?: string
      seek?: string
    } = {}
    const features = ["timestamps", "duration", "seek"]

    const isSmall = computed(() => props.size === "s")
    const isMedium = computed(() => props.size === "m")
    const isLarge = computed(() => props.size === "l")

    const uiStore = useUiStore()
    const shouldBlur = computed(
      () => uiStore.shouldBlurSensitive && props.audio.isSensitive
    )

    return {
      timeFmt,

      features,
      featureNotices,

      isSmall,
      isMedium,
      isLarge,

      shouldBlur,
    }
  },
})
</script>

<style>
.row-track .play-pause {
  @apply flex-shrink-0 rounded-es-sm rounded-ss-sm;
}

.row-track .waveform {
  @apply flex-grow;
  --waveform-background-color: theme("colors.tx");
}

.row-track .waveform {
  @apply rounded-ee-sm rounded-se-sm;
}

.row-track.size-m .waveform {
  @apply h-20;
}

.row-track.size-l .waveform {
  @apply h-14;
}
</style>
