<template>
  <h1
    class="sr-only break-words md:not-sr-only"
    :class="[size === 'large' ? 'heading-1' : 'heading-2']"
  >
    <slot default />
  </h1>
</template>

<script lang="ts">
import { defineComponent, PropType } from "@nuxtjs/composition-api"

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
