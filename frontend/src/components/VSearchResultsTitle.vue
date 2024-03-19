<template>
  <h1
    aria-hidden="true"
    class="hidden break-words md:flex"
    :class="[
      size === 'large'
        ? 'heading-2 lg:heading-1 !leading-none lg:!leading-none'
        : 'heading-2 !leading-none',
    ]"
  >
    <slot default />
  </h1>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

export default defineComponent({
  name: "VSearchResultsTitle",
  props: {
    size: {
      required: false,
      default: "default",
      type: String as PropType<"default" | "large">,
    },
  },
})
</script>

<style scoped>
/* Title case the user's search query */
h1:first-letter {
  text-transform: uppercase;
}
</style>
