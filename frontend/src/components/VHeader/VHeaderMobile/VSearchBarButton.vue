<template>
  <VButton :aria-label="label" size="large" variant="plain--avoid" icon-only>
    <span
      class="group-focus-visible/button:ring-pink-8 group-active/button:ring-pink-8 relative flex h-8 w-8 flex-none items-center justify-center rounded-sm border border-tx group-focus-visible/button:ring group-active/button:ring"
      :class="variant"
    >
      <VIcon
        :name="icon"
        :rtl-flip="rtlFlip"
        class="pointer-events-none"
        :size="6"
      />
      <!--  @slot The element that can show a notification label for the button, can be absolutely positioned  -->
      <slot name="notification" />
    </span>
  </VButton>
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

import type { TranslateResult } from "vue-i18n"

/**
 * The buttons placed inside the mobile search bar in the header.
 * They are based on the VButton, look like they have a smallish focus area
 * (32x32px), but actually have a larger tappable area of 48x48px to comply with
 * accessibility requirements.
 */
export default defineComponent({
  name: "VSearchBarButton",
  components: { VIcon, VButton },
  props: {
    /**
     * The name of the icon.
     */
    icon: {
      type: String,
      required: true,
    },
    /**
     * Whether the icon should be flipped when the page is in RTL mode.
     */
    rtlFlip: {
      type: Boolean,
      default: false,
    },
    /**
     * The label to use as accessible name for the button (aria-label).
     */
    label: {
      type: [String, Object] as PropType<string | TranslateResult>,
      required: true,
    },
    /**
     * The style of the inner area, matches the variants of VButton component.
     */
    variant: {
      type: String as PropType<
        "transparent-dark" | "transparent-gray" | "filled-white" | "filled-gray"
      >,
      default: "transparent-dark",
    },
  },
})
</script>

<style scoped>
.button {
  accent-color: transparent;
}
.button:focus {
  outline: none;
}
.transparent-dark {
  @apply text-gray-12 group-hover/button:bg-gray-12 border-tx bg-tx hover:text-white;
}
.transparent-gray {
  @apply text-gray-12 group-hover/button:bg-gray-12 border-tx bg-tx group-hover/button:bg-opacity-10;
}
.filled-white {
  @apply text-gray-12 group-hover/button:bg-gray-12 border-tx bg-white group-hover/button:text-white;
}

.filled-gray {
  @apply text-gray-12 group-hover/button:bg-gray-12 border-tx bg-dark-charcoal-10 group-hover/button:text-white;
}

.filled-white,
.filled-gray {
  @apply group-focus-visible/button:border-white;
}
</style>
