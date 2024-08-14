<script setup lang="ts">
/**
 * The buttons placed inside the mobile search bar in the header.
 * They are based on the VButton, look like they have a smallish focus area
 * (32x32px), but actually have a larger tappable area of 48x48px to comply with
 * accessibility requirements.
 */
import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

withDefaults(
  defineProps<{
    /**
     * The name of the icon.
     */
    icon: string
    /**
     * Whether the icon should be flipped when the page is in RTL mode.
     */
    rtlFlip?: boolean
    /**
     * The label to use as accessible name for the button (aria-label).
     */
    label: string
    /**
     * The style of the inner area, matches the variants of VButton component.
     */
    variant?:
      | "transparent-dark"
      | "transparent-gray"
      | "filled-white"
      | "filled-gray"
  }>(),
  {
    rtlFlip: false,
    variant: "transparent-dark",
  }
)
</script>

<template>
  <VButton :aria-label="label" size="large" variant="plain--avoid" icon-only>
    <span
      class="relative flex h-8 w-8 flex-none items-center justify-center rounded-sm border border-tx group-focus-visible/button:ring group-focus-visible/button:ring-pink-8 group-active/button:ring group-active/button:ring-pink-8"
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

<style scoped>
.button {
  accent-color: transparent;
}
.button:focus {
  outline: none;
}
.transparent-dark {
  @apply border-tx bg-tx text-default hover:text-over-dark group-hover/button:bg-tertiary;
}
.transparent-gray {
  @apply border-tx bg-tx text-default group-hover/button:bg-tertiary;
}
.filled-white {
  @apply border-tx bg-default text-default group-hover/button:bg-tertiary group-hover/button:text-over-dark;
}

.filled-gray {
  @apply border-tx bg-secondary text-default group-hover/button:bg-tertiary group-hover/button:text-over-dark;
}

.filled-white,
.filled-gray {
  @apply group-focus-visible/button:border-bg-ring;
}
</style>
