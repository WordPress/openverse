<template>
  <svg
    :viewBox="viewBox"
    focusable="false"
    class="v-icon flex-none"
    :class="icon.class"
    aria-hidden="true"
  >
    <use :href="icon.url" />
  </svg>
</template>

<script setup lang="ts">
import { ref, watch } from "vue"

import { useSprite } from "~/composables/use-sprite"

/**
 * Vendored from SVG Sprite Module https://github.com/nuxt-modules/svg-sprite
 * The module had problem with handling the source code that is inside `/src` directory.
 */

const props = withDefaults(
  defineProps<{
    /**
     * The name of the svg. For options, @see "~/assets/svg/sprite/images.svg"
     */
    name: string
    viewBox?: string
  }>(),
  {
    viewBox: "0 0 24 24",
  }
)

if (!props.viewBox.split(" ").every((v) => !isNaN(parseInt(v)))) {
  throw new Error(
    `Invalid viewBox "${props.viewBox}" for icon "${props.name}".`
  )
}

const icon = ref({
  url: "",
  class: "",
})

icon.value = useSprite(`images/${props.name}`)

watch(
  () => props.name,
  (name) => {
    icon.value = useSprite(name)
  }
)
</script>
