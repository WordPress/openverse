<template>
  <VIconButton
    :button-props="buttonProps"
    :icon-props="iconProps"
    :borderless="true"
    :size="size"
    :class="{
      'bg-tx text-white ring-offset-tx focus-slim-tx-yellow hover:bg-white hover:bg-opacity-10':
        variant === 'black',
      '!text-dark-charcoal-70 hover:!text-white':
        variant === 'filled-white-light',
    }"
    :label="label"
    @click="$emit('close')"
  />
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { ButtonVariant } from "~/types/button"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

import type { TranslateResult } from "vue-i18n"

type CloseButtonVariant =
  | "filled-white"
  | "filled-white-light"
  | "filled-transparent"
  | "transparent-gray"
  | "filled-dark"
  | "black"
  | "plain--avoid"

/**
 * The square icon button with a cross in it. Used to close popovers,
 * modals, and other overlays.
 * Must have a label for accessibility.
 */
export default defineComponent({
  name: "VCloseButton",
  components: { VIconButton },
  props: {
    label: {
      type: [String, Object] as PropType<string | TranslateResult>,
      required: true,
    },
    /**
     * The variant of the button. `filled-white-light` is not a VButton variant,
     * it overrides the `filled-white` variant's text color with a lighter color.
     *
     * `black` is a special non-standard button used only on the black
     * background of the internal header.
     *
     * @default "filled-white-light"
     */
    variant: {
      type: String as PropType<CloseButtonVariant>,
      default: "filled-white-light",
    },
    /**
     * The size of the underlying VIconButton.
     */
    size: {
      type: String as PropType<"close" | "small" | "medium" | "large">,
      default: "medium",
    },
    /**
     * Whether to choose `close-small` or `close` (medium) icon.
     *
     * @default "medium"
     */
    iconSize: {
      type: String as PropType<"small" | "medium">,
      default: "small",
    },
  },
  setup(props) {
    const iconProps = computed(() => {
      return { name: props.iconSize === "small" ? "close-small" : "close" }
    })

    const buttonProps = computed<{ variant: ButtonVariant }>(() => {
      const variant =
        props.variant === "black"
          ? "plain--avoid"
          : props.variant === "filled-white-light"
          ? "filled-white"
          : props.variant
      return { variant }
    })

    return {
      buttonProps,
      iconProps,
    }
  },
})
</script>
