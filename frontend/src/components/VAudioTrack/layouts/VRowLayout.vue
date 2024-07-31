<template>
  <!-- `pages/search/audio` has negative margin `-mx-4` to compensate for this padding. -->
  <article
    class="row-track grid p-2 hover:bg-dark-charcoal-06 md:p-4"
    :class="[`size-${size}`, { 'items-start': isSmall }]"
  >
    <div
      class="thumbnail grid overflow-hidden rounded-sm"
      :class="{ 'h-20 w-20': isSmall }"
    >
      <VAudioThumbnail :audio="audio" class="col-span-full row-span-full" />
      <div
        v-show="isSmall"
        class="z-10 col-span-full row-span-full self-end justify-self-start"
      >
        <slot
          name="audio-control"
          size="small"
          layout="row"
          :is-tabbable="false"
        />
      </div>
    </div>

    <div role="document" class="flex min-w-0 flex-shrink-0 flex-col gap-1">
      <h2
        class="decoration-inherit text-gray-12 hover:text-gray-12 line-clamp-1 block overflow-hidden text-ellipsis whitespace-nowrap rounded-sm group-hover:underline"
        :class="[
          { 'blur-text': shouldBlur },
          isSmall ? 'label-bold' : 'description-bold',
        ]"
      >
        {{ shouldBlur ? $t("sensitiveContent.title.audio") : audio.title }}
      </h2>

      <div
        class="flex text-dark-charcoal-70"
        :class="[
          isSmall ? 'caption-regular' : 'label-regular',
          isMedium ? 'flex-row items-center' : 'flex-col gap-1',
        ]"
      >
        <i18n-t
          tag="div"
          keypath="audioTrack.creator"
          scope="global"
          class="line-clamp-1 inline-block overflow-hidden text-ellipsis whitespace-nowrap"
          :class="{ 'blur-text': shouldBlur }"
        >
          <template #creator>{{
            shouldBlur ? $t("sensitiveContent.creator") : audio.creator
          }}</template>
        </i18n-t>
        <!-- Small layout only -->
        <div v-if="isSmall" class="flex flex-col gap-1">
          <div class="flex flex-row">
            <span class="flex">{{ timeFmt(audio.duration || 0, true) }}</span
            ><span v-if="audio.category" class="dot-before">{{
              $t(`filters.audioCategories.${audio.category}`)
            }}</span>
          </div>
          <VLicense :hide-name="true" :license="audio.license" />
        </div>
        <!-- Medium and large layouts -->
        <div v-else class="flex flex-shrink-0 flex-row">
          <span v-if="audio.category" :class="{ 'dot-before': isMedium }">{{
            $t(`filters.audioCategories.${audio.category}`)
          }}</span>
          <VLicense
            :hide-name="!isMd"
            :license="audio.license"
            :class="{ 'dot-before': isMedium || (isLarge && audio.category) }"
          />
        </div>
      </div>
    </div>

    <div
      v-show="!isSmall"
      class="controller flex flex-row"
      :class="{ 'ms-2': isLarge }"
    >
      <slot
        name="audio-control"
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
  </article>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { timeFmt } from "~/utils/time-fmt"
import type { AudioDetail } from "~/types/media"
import { audioFeatures, AudioSize } from "~/constants/audio"

import { useSensitiveMedia } from "~/composables/use-sensitive-media"

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

    const isSmall = computed(() => props.size === "s")
    const isMedium = computed(() => props.size === "m")
    const isLarge = computed(() => props.size === "l")

    const { isHidden: shouldBlur } = useSensitiveMedia(props.audio)

    const uiStore = useUiStore()
    const isMd = computed(() => uiStore.isBreakpoint("md"))

    return {
      timeFmt,

      audioFeatures,
      featureNotices,

      isSmall,
      isMedium,
      isLarge,
      isMd,

      shouldBlur,
    }
  },
})
</script>

<style scoped>
:deep(.audio-control) {
  @apply flex-none rounded-es-sm rounded-ss-sm;
}

:deep(.waveform) {
  @apply w-full rounded-ee-sm rounded-se-sm;
  --waveform-background-color: theme("colors.tx");
}

.row-track.size-s {
  grid-template-columns: 5rem 1fr;
  grid-template-rows: repeat(4, auto);
  @apply gap-x-4;
  grid-template-areas: "thumbnail info-1" "thumbnail info-2" "thumbnail info-3" "thumbnail controller";
}
.row-track.size-m {
  grid-template-columns: 5.9375rem 1fr;
  grid-template-rows: auto auto 3rem;
  @apply gap-x-6;
  grid-template-areas: "thumbnail info-1" "thumbnail info-2" "thumbnail controller";
}
.row-track.size-l {
  grid-template-columns: 4rem 17.5rem 1fr;
  grid-template-rows: auto auto auto;
  @apply gap-x-4;
  grid-template-areas: "thumbnail info-1 controller" "thumbnail info-2 controller" "thumbnail info-3 controller";
}
.row-track .thumbnail {
  grid-area: thumbnail;
}
.row-track .controller {
  grid-area: controller;
}

.row-track.size-m .waveform {
  @apply h-12;
}

.row-track.size-l .waveform {
  @apply h-16;
}

.dot-after {
  @apply relative me-5;
  @apply after:absolute after:-end-3 after:top-[calc(50%-0.125rem)] after:h-1 after:w-1 after:rounded-full after:bg-dark-charcoal-70;
}

.dot-before {
  @apply relative ms-5;
  @apply before:absolute before:-start-3 before:top-[calc(50%-0.125rem)] before:h-1 before:w-1 before:rounded-full before:bg-dark-charcoal-70;
}
</style>
