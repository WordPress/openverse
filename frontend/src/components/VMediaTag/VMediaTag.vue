<template>
  <Component
    :is="tag"
    v-bind="$attrs"
    class="caption-bold md:description-bold inline-flex rounded-full bg-dark-charcoal-10 px-3 py-1 text-dark-blue md:px-4 md:py-2"
  >
    <!-- @slot Content goes here -->
    <slot />
  </Component>
</template>

<script lang="ts">
/**
 * Displays a tag associated with a media item. If set up as a link, it can be
 * used as a link to find other items that are similarly tagged.
 */
import { defineComponent } from "vue"

export default defineComponent({
  name: "MediaTag",
  props: {
    /**
     * the HTML tag or Vue component to use as the root node; A non-interactive
     * span will be rendered unless specified otherwise.
     */
    tag: {
      type: String,
      default: "span",
    },
  },
})
</script>
