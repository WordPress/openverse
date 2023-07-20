<template>
  <!-- Using `flex` to center the group of SVGs inside the bounding box. -->
  <div class="flex flex-row items-center">
    <!-- Using `flex` to place two SVGs side by side. -->
    <span class="inline-flex h-[1em] flex-row gap-[0.4em]" aria-hidden="true">
      <VSvg class="h-full w-auto" viewBox="0 0 50 42" name="logo" />
      <VSvg class="h-full w-auto" viewBox="0 0 215 42" name="brand" />
    </span>
    <!-- 'static' fixes WordPress/openverse#2596 -->
    <span v-if="srText" class="sr-only static">{{ srText }}</span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue"

import VSvg from "~/components/VSvg/VSvg.vue"
/**
 * Render the openverse logo and wordmark next to each other, while being
 * accessible to screen-readers.
 */
export default defineComponent({
  name: "VBrand",
  components: {
    VSvg,
  },
  props: {
    /**
     * the screen-reader text to put inside the component; Can be set to a blank
     * string to not read anything at all.
     */
    srText: {
      type: String,
      required: false,
      default: "Openverse",
    },
  },
})
</script>
