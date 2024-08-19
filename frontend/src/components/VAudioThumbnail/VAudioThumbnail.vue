<script setup lang="ts">
/**
 * Displays the cover art for the audio in a square aspect ratio.
 */
import { useI18n } from "#imports"

import { toRefs, ref, onMounted } from "vue"

import { rand, hash } from "~/utils/prng"
import { lerp, dist, bezier, Point } from "~/utils/math"
import type { AudioDetail } from "~/types/media"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"

const props = defineProps<{
  /**
   * The details of the audio whose artwork is to be shown. The properties
   * `thumbnail`, `title` and `creator` are used.
   */
  audio: AudioDetail
}>()

const { audio } = toRefs(props)
const { isHidden: shouldBlur } = useSensitiveMedia(audio)

const { t } = useI18n({ useScope: "global" })
const helpText = shouldBlur.value
  ? t("sensitiveContent.title.audio")
  : t("audioThumbnail.alt", {
      title: props.audio.title,
      creator: props.audio.creator,
    })

/* Switching */

const imgEl = ref<HTMLImageElement | null>(null)
const isOk = ref(false)
const handleLoad = () => {
  isOk.value = true
}
onMounted(() => {
  isOk.value = Boolean(imgEl.value?.complete && imgEl.value?.naturalWidth)
})

/* Artwork */

const dotCount = 10
const canvasSize = 768
const minRadius = 2
const maxRadius = 27

const random = rand(hash(props.audio.title ?? ""))
const ctrlPts = Array.from(
  { length: 4 },
  (_, idx) => [random() * canvasSize, (idx / 3) * canvasSize] as Point
)

const pointCount = dotCount + 1
const bezierPoints = bezier(ctrlPts, pointCount)

const offset = (i: number) => {
  return i * (canvasSize / (dotCount + 1))
}
const radius = (i: number, j: number) => {
  const bezierPoint = bezierPoints[i]
  const distance = dist([0, bezierPoint], [0, offset(j)])
  const maxFeasibleDistance = canvasSize * ((dotCount - 1) / (dotCount + 1))
  return lerp(maxRadius, minRadius, distance / maxFeasibleDistance)
}
</script>

<template>
  <!-- Should be wrapped by a fixed-width parent -->
  <div class="relative h-0 w-full overflow-hidden pt-full" :title="helpText">
    <!-- Programmatic thumbnail -->
    <svg
      v-if="!isOk"
      class="absolute inset-0 bg-complementary"
      :viewBox="`0 0 ${canvasSize} ${canvasSize}`"
    >
      <template v-for="i in dotCount">
        <circle
          v-for="j in dotCount"
          v-show="!shouldBlur"
          :key="`${i}-${j}`"
          class="fill-gray-12"
          :cx="offset(j)"
          :cy="offset(i)"
          :r="radius(i, j)"
        />
      </template>
    </svg>

    <!-- The element that blurs the programmatic thumbnail -->
    <div
      v-show="shouldBlur && !audio.thumbnail"
      class="bg-blur absolute bg-complementary"
    />

    <div v-show="audio.thumbnail && isOk" class="thumbnail absolute inset-0">
      <img
        ref="imgEl"
        class="h-full w-full overflow-clip object-cover object-center duration-200 motion-safe:transition-[filter,transform]"
        :class="{ 'scale-150 blur-image': shouldBlur }"
        :src="audio.thumbnail"
        :alt="helpText"
        @load="handleLoad"
      />
    </div>

    <VIcon
      v-show="shouldBlur"
      name="eye-closed"
      class="absolute left-[calc(50%-0.75rem)] top-[calc(50%-0.75rem)]"
    />
  </div>
</template>
