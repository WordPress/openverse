<script setup lang="ts">
import { useNuxtApp } from "#imports"

import type { GallerySet } from "~/types/home-gallery"

const props = defineProps<{
  idx: number
  dimens: number
  set: GallerySet
  image: {
    id: string
    src: string
    title: string
    url: string
  }
}>()

const { $sendCustomEvent } = useNuxtApp()
const handleClick = (id: string) => {
  $sendCustomEvent("CLICK_HOME_GALLERY_IMAGE", {
    set: props.set,
    id,
  })
}
</script>

<template>
  <VLink
    class="home-cell rounded-full p-1 focus-visible:bg-default"
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
</template>
