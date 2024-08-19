<script lang="ts">
import { defineComponent } from "vue"

import VSvg from "~/components/VSvg/VSvg.vue"

/**
 * A simple Openverse logo component, visually hidden from screen-reader users.
 * Implementations should wrap this icon with appropriate sr-only text or an aria-label.
 */
export default defineComponent({
  name: "VBrand",
  components: {
    VSvg,
  },
})
</script>

<template>
  <!-- Using `flex` to place two SVGs side by side, centered. -->
  <span
    class="flex h-[1em] flex-row items-center gap-x-[0.4em]"
    aria-hidden="true"
  >
    <VSvg class="h-full w-auto" viewBox="0 0 50 42" name="logo" />
    <VSvg class="h-full w-auto" viewBox="0 0 215 42" name="brand" />
  </span>
</template>
