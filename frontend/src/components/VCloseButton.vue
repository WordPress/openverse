<template>
  <VIconButton
    :button-props="{
      variant:
        variant === 'black'
          ? 'plain--avoid'
          : variant === 'filled-white-light'
          ? 'filled-white'
          : variant,
    }"
    :icon-props="{ iconPath }"
    :borderless="true"
    :size="size"
    :class="{
      'bg-black text-white ring-offset-black focus-slim-tx-yellow hover:border hover:border-white':
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

import VIconButton from "~/components/VIconButton/VIconButton.vue"

import type { TranslateResult } from "vue-i18n"

import closeIcon from "~/assets/icons/close.svg"
import closeIconSmall from "~/assets/icons/close-small.svg"

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
      type: String as PropType<
        | "filled-white"
        | "filled-white-light"
        | "filled-transparent"
        | "filled-dark"
        | "black"
      >,
      default: "filled-white-light",
    },
    /**
     * The size of the underlying VIconButton.
     */
    size: {
      type: String as PropType<"small" | "medium" | "large">,
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
    const iconPath = computed<string>(() => {
      return props.iconSize === "small" ? closeIconSmall : closeIcon
    })

    return {
      iconPath,
    }
  },
})
</script>
