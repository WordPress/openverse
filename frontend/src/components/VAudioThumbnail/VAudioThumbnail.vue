<template>
  <!-- Should be wrapped by a fixed-width parent -->
  <div
    class="relative h-0 w-full overflow-hidden bg-yellow pt-full"
    :title="helpText"
  >
    <!-- Programmatic thumbnail -->
    <svg
      class="absolute inset-0"
      :class="{ hidden: shouldBlur && isOk }"
      :viewBox="`0 0 ${canvasSize} ${canvasSize}`"
    >
      <template v-for="i in dotCount">
        <circle
          v-for="j in dotCount"
          :key="`${i}-${j}`"
          class="fill-dark-charcoal"
          :cx="offset(j)"
          :cy="offset(i)"
          :r="radius(i, j)"
        />
      </template>
    </svg>

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
  </div>
</template>

<script lang="ts">
import { toRefs, ref, onMounted, defineComponent, PropType } from "vue"

import { rand, hash } from "~/utils/prng"
import { lerp, dist, bezier, Point } from "~/utils/math"
import type { AudioDetail } from "~/types/media"
import { useNuxtI18n } from "~/composables/use-i18n"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"

/**
 * Displays the cover art for the audio in a square aspect ratio.
 */
export default defineComponent({
  name: "VAudioThumbnail",
  props: {
    /**
     * the details of the audio whose artwork is to be shown; The properties
     * `thumbnail`, `title` and `creator` are used.
     */
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
  },
  setup(props) {
    const { audio } = toRefs(props)
    const { isHidden: shouldBlur } = useSensitiveMedia(audio)

    const i18n = useNuxtI18n()
    const helpText = shouldBlur.value
      ? i18n.t("sensitiveContent.title.audio")
      : i18n.t("audioThumbnail.alt", {
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

    return {
      imgEl,
      isOk,
      handleLoad,

      canvasSize,
      dotCount,
      offset,
      radius,
      helpText,

      shouldBlur,
    }
  },
})
</script>
