<template>
  <!-- `pages/search/audio` has negative margin `-mx-4` to compensate for this padding. -->
  <article
    class="row-track flex flex-row p-2 hover:bg-dark-charcoal-06 md:p-4"
    :class="[`size-${size}`, { 'items-start': isSmall }]"
  >
    <div
      class="grid flex-none overflow-hidden rounded-sm"
      :class="isMedium ? 'me-6 w-[95px]' : isSmall ? 'me-4 w-20' : 'me-4 w-16'"
    >
      <VAudioThumbnail :audio="audio" class="col-span-full row-span-full" />
      <div
        v-show="isSmall"
        class="z-10 col-span-full row-span-full self-end justify-self-start"
      >
        <slot
          name="play-pause"
          size="small"
          layout="row"
          :is-tabbable="false"
        />
      </div>
    </div>

    <div
      class="flex-grow"
      :class="{
        'flex flex-row gap-8': isLarge,
        'flex flex-col justify-between': isMedium,
      }"
    >
      <div class="flex-shrink-0" :class="{ 'w-70': isLarge }" role="document">
        <h2
          class="decoration-inherit line-clamp-1 block h-[18px] rounded-sm p-px text-dark-charcoal hover:text-dark-charcoal focus:outline-none focus:ring focus:ring-pink group-hover:underline"
          :class="{
            'description-bold': isMedium || isLarge,
            'label-bold': isSmall,
            'blur-text': shouldBlur,
          }"
        >
          {{ shouldBlur ? $t("sensitiveContent.title.audio") : audio.title }}
        </h2>

        <div
          class="mt-1 flex text-dark-charcoal-70"
          :class="[
            isSmall ? 'caption-regular' : 'label-regular',
            isMedium ? 'flex-row items-center' : 'flex-col gap-1',
          ]"
        >
          <i18n
            tag="div"
            path="audioTrack.creator"
            class="flex"
            :class="{ 'blur-text': shouldBlur, 'dot-after': isMedium }"
          >
            <template #creator>{{
              shouldBlur ? $t("sensitiveContent.creator") : audio.creator
            }}</template>
          </i18n>
          <div class="flex" :class="isSmall ? 'flex-col' : 'flex-row'">
            <div
              class="flex flex-row"
              :class="isSmall ? 'mb-1' : !!audio.category ? 'dot-after' : ''"
            >
              <span v-if="isSmall" class="dot-after flex">{{
                timeFmt(audio.duration || 0, true)
              }}</span
              ><span v-if="audio.category">{{
                $t(`filters.audioCategories.${audio.category}`)
              }}</span>
            </div>
            <VLicense :hide-name="isSmall" :license="audio.license" />
          </div>
        </div>
      </div>

      <div
        v-show="!isSmall"
        class="flex flex-row"
        :class="{ 'flex-grow': isLarge }"
      >
        <slot
          name="play-pause"
          :size="isLarge ? 'large' : 'medium'"
          layout="row"
          :is-tabbable="false"
        />
        <slot
          name="controller"
          :features="audioFeatures"
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
import { audioFeatures, AudioSize } from "~/constants/audio"

import { useSensitiveMedia } from "~/composables/use-sensitive-media"

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

    const isSmall = computed(() => props.size === "s")
    const isMedium = computed(() => props.size === "m")
    const isLarge = computed(() => props.size === "l")

    const playPauseSize = computed(() => {
      if (props.size === undefined) {
        console.log("Why isn't there a size prop?", props.size)
        return "medium"
      }
      return { l: "large", m: "medium", s: "small" }[props.size]
    })

    const { isHidden: shouldBlur } = useSensitiveMedia(props.audio)

    return {
      timeFmt,

      audioFeatures,
      featureNotices,

      isSmall,
      isMedium,
      isLarge,
      playPauseSize,

      shouldBlur,
    }
  },
})
</script>

<style scoped>
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
  @apply h-12;
}

.row-track.size-l .waveform {
  @apply h-16;
}
.dot-after {
  @apply after:me-2 after:ms-2 after:inline-flex after:h-1 after:w-1 after:self-center after:rounded-full after:bg-dark-charcoal-70 after:text-2xl after:content-[""];
}
.dot-before {
  @apply before:me-2 before:ms-2 before:inline-flex before:h-1 before:w-1 before:self-center before:rounded-full before:bg-dark-charcoal-70 before:text-base before:content-[""];
}
</style>
