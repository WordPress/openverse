<template>
  <VButton
    :aria-label="label"
    :size="size"
    :variant="variant"
    class="icon-button"
    icon-only
    v-on="$listeners"
  >
    <slot name="default" :icon-size="6" />
    <VIcon
      v-if="iconProps"
      class="pointer-events-none"
      :size="6"
      v-bind="iconProps"
    />
  </VButton>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { ButtonSize, ButtonVariant } from "~/types/button"

import VIcon, { type IconProps } from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"

import type { TranslateResult } from "vue-i18n"

/**
 * The icon-only version of VButton component. In some cases, VButton is replaced
 * with VIconButton in small breakpoints.
 */
export default defineComponent({
  name: "VIconButton",
  components: { VIcon, VButton },
  props: {
    /**
     * The size of the button, matches the sizes of VButton component.
     */
    size: {
      type: String as PropType<Exclude<ButtonSize, "disabled">>,
      required: true,
    },
    /**
     * The visual variant of the button, matches the variants of VButton component.
     */
    variant: {
      type: String as PropType<ButtonVariant>,
      required: true,
    },
    /**
     * Props to pass down to the `VIcon` component nested inside the button.
     * See documentation on `VIcon`.
     */
    iconProps: {
      type: Object as PropType<IconProps>,
      required: false,
    },
    /**
     * The label used for accessibility purposes.
     */
    label: {
      type: [String, Object] as PropType<string | TranslateResult>,
      required: true,
    },
  },
})
</script>
