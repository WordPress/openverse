<template>
  <VButton
    v-bind="buttonProps"
    :aria-label="label"
    size="disabled"
    :variant="variant"
    class="icon-button"
    :class="buttonSizeClasses"
    :type="type"
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
import { computed, defineComponent, PropType } from "vue"

import type { ButtonSize, ButtonType, ButtonVariant } from "~/types/button"

import VIcon, { type IconProps } from "~/components/VIcon/VIcon.vue"
import VButton, { type ButtonProps } from "~/components/VButton.vue"

import type { TranslateResult } from "vue-i18n"

const sizes = {
  small: 8,
  medium: 10,
  large: 12,
}

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
     * Props to pass down to the `VButton` component nested inside the button.
     * See documentation on `VButton`.
     */
    buttonProps: {
      type: Object as PropType<Omit<ButtonProps, "size">>,
      default: () => ({ variant: "transparent-tx" }),
    },
    /**
     * the label for the button; This is used for accessibility purposes.
     */
    label: {
      type: [String, Object] as PropType<string | TranslateResult>,
      required: true,
    },
  },
  setup(props, { attrs }) {
    const type = (attrs["type"] ?? "button") as ButtonType

    const buttonSizeClasses = computed(
      () => `w-${sizes[props.size]} h-${sizes[props.size]}`
    )

    return {
      type,

      buttonSizeClasses,
    }
  },
})
</script>
