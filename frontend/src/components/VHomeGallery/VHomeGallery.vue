<script setup lang="ts">
/**
 * Displays a grid of images for the homepage, with each image linking to its
 * single result page. The number of columns automatically adjusts to the width
 * of the container upto a max of 5.
 */
import { useLocalePath, useRouter } from "#imports"

import { computed, ref } from "vue"

import { useReducedMotion } from "~/composables/use-reduced-motion"
import useResizeObserver from "~/composables/use-resize-observer"

import type { GallerySet } from "~/types/home-gallery"

import VGalleryImage from "~/components/VHomeGallery/VGalleryImage.vue"

import untypedImageInfo from "~/assets/homepage_images.json"

const props = withDefaults(defineProps<{ set?: GallerySet }>(), {
  set: "random",
})

type HomepageImage = { id: string; title: string; src: string }
type ImageSet = {
  key: GallerySet
  term: string
  images: HomepageImage[]
}
const imageInfo = untypedImageInfo as unknown as {
  sets: ImageSet[]
}

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
</script>

<template>
  <!-- Wrapper element to center the grid if space is more than 5 columns. -->
  <div ref="el" class="flex-row items-center justify-end 2xl:justify-center">
    <!-- Image grid only occupies as much width as needed. -->
    <div
      class="home-gallery inline-grid grid-flow-col grid-rows-3 gap-8"
      :style="{
        gap: `${space}px`,
        gridTemplateColumns: `repeat(${columnCount}, minmax(0, 1fr))`,
      }"
    >
      <ClientOnly>
        <template v-if="prefersReducedMotion">
          <VGalleryImage
            v-for="(image, idx) in imageList"
            :key="image.url"
            :image="image"
            :set="imageSet.key"
            :idx="idx"
            :dimens="dimens"
          />
        </template>
        <Transition
          v-for="(image, idx) in imageList"
          v-else
          :key="idx"
          enter-active-class="transition-opacity delay-[var(--delay)] duration-500"
          leave-active-class="transition-opacity delay-[var(--delay)] duration-500"
          enter-from-class="opacity-0"
          leave-to-class="opacity-0"
          mode="out-in"
          appear
        >
          <VGalleryImage
            :idx="idx"
            :dimens="dimens"
            :image="image"
            :set="imageSet.key"
            :class="idx >= imageCount ? 'hidden' : 'block'"
          />
        </Transition>
      </ClientOnly>
    </div>
  </div>
</template>
