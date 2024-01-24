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

const props = withDefaults(
  defineProps<{
    /**
     * the path to the icon SVG; In a bundled application like Openverse,
     * importing an SVG should give us the path to the file.
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
