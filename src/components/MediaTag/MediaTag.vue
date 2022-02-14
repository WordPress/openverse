<template>
  <Component
    :is="tag"
    v-bind="$attrs"
    class="text-dark-blue text-sr md:text-sm font-semibold px-2 md:px-3 py-1 md:py-2 bg-dark-charcoal-10 rounded-full leading-none inline-flex"
  >
    <!-- @slot Content goes here -->
    <slot />
  </Component>
</template>

<script>
/**
 * Displays a tag associated with a media item. If set up as a link, it can be
 * used as a link to find other items that are similarly tagged.
 */
export default {
  name: 'MediaTag',
  props: {
    /**
     * the HTML tag or Vue component to use as the root node; A non-interactive
     * span will be rendered unless specified otherwise.
     */
    tag: {
      type: String,
      default: 'div',
    },
  },
}
</script>
