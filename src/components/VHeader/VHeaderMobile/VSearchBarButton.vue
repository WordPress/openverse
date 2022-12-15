<template>
  <VIconButton
    class="border-tx bg-tx"
    :button-props="{ variant: 'plain--avoid' }"
    v-on="$listeners"
  >
    <template #default="{ iconSize }">
      <span
        class="relative flex flex-shrink-0 flex-grow-0 items-center justify-center rounded-sm group-focus-visible:ring group-focus-visible:ring-pink group-active:ring group-active:ring-pink"
        :class="[`h-${innerSize} w-${innerSize}`, innerAreaClasses]"
      >
        <VIcon
          :icon-path="iconPath"
          :rtl-flip="rtlFlip"
          class="pointer-events-none"
          :size="iconSize"
        />
        <!--  @slot The element that can show a notification label for the button, can be absolutely positioned  -->
        <slot name="notification" />
      </span>
    </template>
  </VIconButton>
</template>
<script lang="ts">
import { defineComponent, PropType } from "@nuxtjs/composition-api"

import VIcon from "~/components/VIcon/VIcon.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

/**
 * The buttons placed inside the mobile search bar in the header.
 * They are based on the VIconButton, look like they have a smallish focus area
 * (32x32px), but actually have a larger tappable area of 48x48px to comply with
 * accessibility requirements.
 */
export default defineComponent({
  name: "VSearchBarButton",
  components: { VIcon, VIconButton },
  props: {
    /**
     * The path for the icon.
     */
    iconPath: {
      type: String,
      required: true,
    },
    /**
     * The size of the inner area that has a different color,
     * sometimes only when interactive.
     */
    innerSize: {
      type: Number as PropType<6 | 8>,
      default: 8,
    },
    /**
     * The classes to apply to the inner area for styling resting/hover states.
     */
    innerAreaClasses: {
      type: String,
      default: "",
    },
    /**
     * Whether the icon should be flipped when the page is in RTL mode.
     */
    rtlFlip: {
      type: Boolean,
      default: false,
    },
  },
})
</script>
