<template>
  <svg
    class="v-icon h-6 w-6"
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
      type: String,
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
  },
}
</script>
