<template>
  <!-- Using `flex` to center the group of SVGs inside the bounding box. -->
  <div class="flex flex-row items-center">
    <!-- Using `flex` to place two SVGs side by side. -->
    <span class="inline-flex h-[1em] flex-row gap-[0.4em]" aria-hidden="true">
      <OpenverseLogo class="h-full w-auto" />
      <OpenverseBrand class="h-full w-auto" />
    </span>
    <span v-if="srText" class="sr-only">{{ srText }}</span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue"

import OpenverseLogo from "~/assets/logo.svg?inline"
import OpenverseBrand from "~/assets/brand.svg?inline"

/**
 * Render the openverse logo and wordmark next to each other, while being
 * accessible to screen-readers.
 */
export default defineComponent({
  name: "VBrand",
  components: {
    OpenverseLogo,
    OpenverseBrand,
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
