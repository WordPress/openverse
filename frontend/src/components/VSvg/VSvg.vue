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

<script lang="ts" setup>
import { ref, watch } from "vue"

import { useSprite } from "~/composables/use-sprite"
/**
 * Displays the given icon in a 24px × 24px square.
 */
const props = defineProps({
  /**
   * the path to the icon SVG; In a bundled application like Openverse,
   * importing an SVG should give us the path to the file.
   */
  /**
   * In `jest` our icons get transformed to Vue components
   */
  name: {
    type: String,
    required: true,
  },
  viewBox: {
    type: String,
    default: "0 0 24 24",
    validator(value: string) {
      return value.split(" ").every((v) => {
        return !isNaN(parseInt(v))
      })
    },
  },
})

const icon = ref({
  url: "",
  class: "",
})

icon.value = await useSprite(`images/${props.name}`)

watch(
  () => props.name,
  async (name) => {
    icon.value = await useSprite(name)
  }
)
</script>
