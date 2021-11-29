<template>
  <svg
    class="v-icon"
    :class="[`w-${size}`, `h-${size}`, { 'rtl-flip': rtlFlip }]"
    xmlns="http://www.w3.org/2000/svg"
    :viewBox="viewBox"
    aria-hidden="true"
    focusable="false"
  >
    <use :href="`${iconPath}#${gId}`" />
  </svg>
</template>

<script>
/**
 * Displays the given icon in a 24px × 24px square.
 */
export default {
  name: 'VIcon',
  props: {
    /**
     *
     */
    viewBox: {
      type: String,
      default: '0 0 24 24',
    },
    /**
     * the path to the icon SVG; In a bundled application like Openverse,
     * importing an SVG should give us the path to the file.
     */
    iconPath: {
      /**
       * In `jest` our icons get transformed to Vue components
       */
      type: process.env.NODE_ENV === 'test' ? Object : String,
      required: true,
    },
    /**
     * the ID of the `g` element to import from the icon; This element should
     * ideally have the `id` as "icon" and the `fill` as `currentColor`.
     */
    gId: {
      type: String,
      default: 'icon',
    },
    /**
     * whether to flip the icon for RTL languages; This generally makes sense
     * for directional icons such as those involving arrows.
     */
    rtlFlip: {
      type: Boolean,
      default: false,
    },
    /**
     * the size of the icon in terms of the Tailwind height and width scale; The
     * icon, being square, uses this for both dimensions.
     */
    size: {
      type: Number,
      default: 6,
    },
  },
}
</script>

<style scoped>
[dir='rtl'] .v-icon.rtl-flip {
  @apply transform -scale-x-100;
}
</style>
