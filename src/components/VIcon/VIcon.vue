<template>
  <svg
    class="v-icon flex-shrink-0 flex-grow-0"
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
     * The size of the icon based on tailwind values. Possible values:
     * 4 - 1rem, 5 - 1.25rem, 6 - 1.5rem.
     *
     * @default 6
     */
    size: {
      type: Number,
      default: 6,
      validator: (val) => [4, 5, 6].includes(val),
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
}
</script>

<style scoped>
[dir='rtl'] .v-icon.rtl-flip {
  @apply transform -scale-x-100;
}
</style>
