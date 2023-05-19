<template>
  <SvgIcon :name="`images/${name}`" aria-hidden="true" focusable="false" />
</template>

<script lang="ts">
import { defineComponent } from "vue"
/**
 * Displays the given SVG image.
 */
export default defineComponent({
  name: "VIcon",
  props: {
    /**
     * name of the SVG in `assets/svg/raw/images`
     */
    name: {
      type: String,
      required: true,
    },
  },
})
</script>
