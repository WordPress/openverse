<template>
  <SvgIcon
    class="v-icon flex-none"
    :class="[`w-${size}`, `h-${size}`, { 'rtl-flip': rtlFlip }]"
    :name="name"
    aria-hidden="true"
    focusable="false"
  />
</template>

<script lang="ts">
import { defineComponent } from "vue"

export type IconProps = {
  name: string
  viewBox?: string
  gId?: string
  size?: number
  rtlFlip?: boolean
}

/**
 * Displays the given icon in a 24px × 24px square.
 */
export default defineComponent({
  name: "VIcon",
  props: {
    /**
     *
     */
    viewBox: {
      type: String,
      default: "0 0 24 24",
    },
    /**
     * the path to the icon SVG; In a bundled application like Openverse,
     * importing an SVG should give us the path to the file.
     */
    name: {
      /**
       * In `jest` our icons get transformed to Vue components
       */
      type: String,
      required: true,
    },
    /**
     * the ID of the `g` element to import from the icon; This element should
     * ideally have the `id` as "icon" and the `fill` as `currentColor`.
     */
    gId: {
      type: String,
      default: "icon",
    },
    /**
     * The size of the icon based on tailwind values. Possible values:
     * 4 - 1rem, 5 - 1.25rem, 6 - 1.5rem, 8 - 2rem, 12 - 3rem.
     *
     * @default 6
     */
    size: {
      type: Number,
      default: 6,
      validator: (val: number) => [4, 5, 6, 8, 12].includes(val),
    },
    /**
     * whether to flip the icon for RTL languages; This generally makes sense
     * for directional icons such as those involving arrows.
     */
    rtlFlip: {
      type: Boolean,
      default: false,
    },
  },
})
</script>

<style scoped>
[dir="rtl"] .v-icon.rtl-flip {
  @apply -scale-x-100 transform;
}
</style>
