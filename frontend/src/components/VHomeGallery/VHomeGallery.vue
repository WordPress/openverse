<script lang="ts">
import { useLocalePath, useRouter } from "#imports"

import { computed, defineComponent, PropType, ref } from "vue"

import { useReducedMotion } from "~/composables/use-reduced-motion"
import { useAnalytics } from "~/composables/use-analytics"
import useResizeObserver from "~/composables/use-resize-observer"

import VLink from "~/components/VLink.vue"

import imageInfo from "~/assets/homepage_images.json"

export const GALLERY_SETS = [
  "universe",
  "pottery",
  "olympics",
  "random",
] as const
export type GallerySet = (typeof GALLERY_SETS)[number]

/**
 * Displays a grid of images for the homepage, with each image linking to its
 * single result page. The number of columns automatically adjusts to the width
 * of the container upto a max of 5.
 */
export default defineComponent({
  name: "VHomeGallery",
  components: { VLink },
  props: {
    /**
     * the set of images to use for the gallery grid
     */
    set: {
      type: String as PropType<GallerySet>,
      required: false,
      default: "random",
      validator: (val: GallerySet) => GALLERY_SETS.includes(val),
    },
  },
  setup(props) {
    const localePath = useLocalePath()
    const router = useRouter()
    const prefersReducedMotion = useReducedMotion()

    const dimens = 152 // px
    const space = 24 // px; 32px space - 4px padding on both sides

    const rowCount = 3
    const columnCount = computed(() =>
      Math.min(
        5, // Grid cannot exceed 5 columns as we only have 15 images.
        Math.floor((gridDimens.value.width + space) / (dimens + space))
      )
    )

    const el = ref<HTMLElement | null>(null) // template ref
    const { dimens: gridDimens } = useResizeObserver(el)

    const imageSet = computed(() =>
      props.set === "random"
        ? imageInfo.sets[Math.floor(Math.random() * imageInfo.sets.length)]
        : (imageInfo.sets.find((item) => (item.key = props.set)) ??
          imageInfo.sets[0])
    )
    const imageList = computed(() => {
      return imageSet.value.images.map((image, idx) => ({
        ...image,
        src: `/homepage_images/${imageSet.value.key}/${idx + 1}.png`,
        url: router.resolve(
          localePath({
            name: "image-id",
            params: { id: image.id },
          })
        ).href,
      }))
    })
    const imageCount = computed(() => columnCount.value * rowCount)

    const { sendCustomEvent } = useAnalytics()
    const handleClick = (id: string) => {
      sendCustomEvent("CLICK_HOME_GALLERY_IMAGE", {
        set: imageSet.value.key,
        id,
      })
    }

    return {
      el,

      dimens,
      space,

      imageCount,
      columnCount,
      imageList,

      prefersReducedMotion,

      handleClick,
    }
  },
})
</script>

<template>
  <!-- Wrapper element to center the grid if space is more than 5 columns. -->
  <div
    ref="el"
    class="mx-10 me-12 flex flex-row items-center justify-end 2xl:justify-center"
  >
    <!-- Image grid only occupies as much width as needed. -->
    <div
      class="home-gallery inline-grid grid-flow-col grid-rows-3 gap-8"
      :style="{
        gap: `${space}px`,
        gridTemplateColumns: `repeat(${columnCount}, minmax(0, 1fr))`,
      }"
    >
      <ClientOnly>
        <Transition
          v-for="(image, idx) in imageList"
          :key="idx"
          enter-active-class="transition-opacity delay-[var(--delay)] duration-500"
          leave-active-class="transition-opacity delay-[var(--delay)] duration-500"
          enter-from-class="opacity-0"
          leave-to-class="opacity-0"
          mode="out-in"
          appear
        >
          <VLink
            class="home-cell rounded-full p-1 focus-visible:bg-default"
            :class="idx >= imageCount ? 'hidden' : 'block'"
            :style="{ '--delay': `${idx * 0.05}s` }"
            :href="image.url"
            @click="handleClick(image.id)"
          >
            <img
              :height="dimens"
              :width="dimens"
              :src="image.src"
              :alt="image.title"
              :title="image.title"
            />
          </VLink>
        </Transition>
      </ClientOnly>
    </div>
  </div>
</template>
