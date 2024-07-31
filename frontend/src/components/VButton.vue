<template>
  <Component
    :is="as"
    :type="typeAttribute"
    class="group/button button flex appearance-none items-center justify-center rounded-sm no-underline"
    :class="[
      variantClass,
      connectionStyles,
      size,
      {
        'icon-only': iconOnly,
        'icon-start': hasIconStart,
        'icon-end': hasIconEnd,
        border: !isPlainDangerous,
        'focus-visible:outline-tx': isPlainDangerous,
        'focus-slim-filled': isFocusSlimFilled,
        'focus-slim-tx': isFocusSlimTx,
      },
    ]"
    :aria-pressed="pressed"
    :aria-disabled="ariaDisabled"
    :disabled="disabledAttribute"
  >
    <!--
      @slot The content of the button
    -->
    <slot />
  </Component>
</template>

<script lang="ts">
import { defineComponent, watch, computed, PropType } from "vue"

import { warn } from "~/utils/console"

import type { ProperlyExtractPropTypes } from "~/types/prop-extraction"
import {
  ButtonConnections,
  buttonForms,
  ButtonSize,
  ButtonType,
  ButtonVariant,
} from "~/types/button"
import type { ButtonForm } from "~/types/button"

import { skipToContentTargetId } from "~/constants/window"

import VLink from "~/components/VLink.vue"

export type ButtonProps = ProperlyExtractPropTypes<
  NonNullable<(typeof VButton)["props"]>
>

/**
 * A button component that behaves just like a regular HTML `button` element
 * aside from pre-applied styles based on the passed in variant.
 *
 * All props available for the basic `button` component are available here as
 * well, including an `as` prop which allows for component polymorphism. The
 * most common use case for this prop is to turn the `VButton` component into
 * an `anchor` element, so that you can render a link instead of a `button`.
 *
 * The accessibility helpers on this component are critical and are completely
 * adapted from Reakit's Button, Clickable, and Tabbable component implementations.
 */
const VButton = defineComponent({
  name: "VButton",
  components: { VLink },
  props: {
    /**
     * Passed to `component :is` to allow the button to *appear* as a button but
     * work like another element (like an `anchor`). May only be either `button` or `VLink`.
     * `anchor` is only supported for the `VSkipToContentButton` component that uses
     * a hash URL (`skipToContentTargetId`).
     *
     * We do not support other elements because their use cases are marginal, and they
     * add complexity that we can avoid otherwise.
     *
     * We also don't allow any old Vue component because Vue does not have ref-forwarding,
     * so we wouldn't be able to detect the type of the DOM node that is ultimately rendered
     * by any Vue component passed.
     *
     * @default 'button'
     */
    as: {
      type: String as PropType<ButtonForm>,
      default: "button",
      validate: (val: ButtonForm) => buttonForms.includes(val),
    },
    /**
     * The variant of the button.
     *
     * Plain removes all styles except the focus ring. The button
     * should set a border color, otherwise the browser default is used.
     * Plain--avoid removes _all_ styles including the focus ring.
     */
    variant: {
      type: String as PropType<ButtonVariant>,
      required: true,
    },
    /**
     * Allows for programmatically setting the pressed state of a button,
     * i.e., in the case of a button opening a menu.
     */
    pressed: {
      type: Boolean,
      default: undefined,
    },
    /**
     * The size of the button. `disabled` removes all internal padding allowing
     * the consumer of the component to determine the padding.
     *
     * @default 'medium'
     */
    size: {
      type: String as PropType<ButtonSize>,
      required: true,
    },
    /**
     * Whether the button is disabled. Used alone this will only
     * visually effect the button but will not "truly" disable the
     * button unless the `focusable` prop is also set to `false`.
     *
     * @default false
     */
    disabled: {
      type: Boolean,
      default: false,
    },
    /**
     * Whether the button is focusable when disabled. Should be `false`
     * in almost all cases except when a button needs to be focusable
     * while still being disabled (in the case of a form submit button
     * that is disabled due to an incomplete form for example).
     *
     * @default false
     */
    focusableWhenDisabled: {
      type: Boolean,
      default: false,
    },
    /**
     * The HTML `type` attribute for the button. Ignored if `as` is
     * passed as anything other than `"button"`.
     *
     * @default 'button'
     */
    type: {
      type: String as PropType<ButtonType>,
      default: "button",
    },
    /**
     * Whether the button is connected to another control and needs to have no rounded
     * borders at that edge.
     *
     * @default []
     */
    connections: {
      type: Array as PropType<ButtonConnections[]>,
      default: () => [] as ButtonConnections[],
    },
    /**
     * Whether the button has an icon at the inline start of the button.
     *
     * @default false
     */
    hasIconStart: {
      type: Boolean,
      default: false,
    },
    /**
     * Whether the button has an icon at the inline end of the button.
     *
     * @default false
     */
    hasIconEnd: {
      type: Boolean,
      default: false,
    },
    /**
     * If the button is only an icon, width is set to height, and padding is removed.
     */
    iconOnly: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, { attrs }) {
    const typeAttribute = computed<ButtonType | undefined>(() =>
      ["VLink", "a"].includes(props.as) ? undefined : props.type
    )

    const connectionStyles = computed(() =>
      props.connections
        .map((connection) => `connection-${connection}`)
        .join(" ")
    )

    const isActive = computed(() => {
      return props.pressed || attrs["aria-pressed"] || attrs["aria-expanded"]
    })
    const variantClass = computed(() => {
      if (
        isActive.value &&
        ["bordered-white", "transparent-dark"].includes(props.variant)
      ) {
        return `${props.variant}-pressed`
      }
      return props.variant
    })

    const isPlainDangerous = computed(() => {
      return props.variant === "plain--avoid"
    })
    const isFocusSlimFilled = computed(() => {
      return props.variant.startsWith("filled-")
    })
    const isFocusSlimTx = computed(() => {
      return (
        props.variant.startsWith("bordered-") ||
        props.variant.startsWith("transparent-") ||
        props.variant === "plain"
      )
    })

    const supportsDisabledAttribute = computed(() => props.as !== "VLink")

    const ariaDisabled = computed<true | undefined>(
      () =>
        // If disabled and focusable then use `aria-disabled` instead of the `disabled` attribute to allow
        // the button to still be tabbed into by screen reader users
        (props.disabled && props.focusableWhenDisabled) || undefined
    )

    const disabledAttribute = computed<true | undefined>(() => {
      const trulyDisabled = props.disabled && !props.focusableWhenDisabled

      return (trulyDisabled && supportsDisabledAttribute.value) || undefined
    })

    watch(
      () => props.as,
      (as) => {
        if (
          ["a", "NuxtLink"].includes(as) &&
          attrs.href !== `#${skipToContentTargetId}`
        ) {
          warn(
            `Please use \`VLink\` with an \`href\` prop instead of ${as} for the button component`
          )
        }
      },
      { immediate: true }
    )

    return {
      variantClass,
      connectionStyles,
      disabledAttribute,
      ariaDisabled,
      typeAttribute,
      isActive,

      isPlainDangerous,
      isFocusSlimFilled,
      isFocusSlimTx,
    }
  },
})

export default VButton
</script>

<style scoped>
.button[disabled="disabled"],
.button[aria-disabled="true"] {
  @apply cursor-not-allowed;
}

a.button {
  @apply no-underline hover:no-underline;
}

.connection-start {
  @apply rounded-s-none;
}
.connection-end {
  @apply rounded-e-none;
}
.connection-top {
  @apply rounded-se-none rounded-ss-none;
}
.connection-bottom {
  @apply rounded-ee-none rounded-es-none;
}

.filled-pink-8 {
  @apply bg-pink-8 border-tx text-white hover:bg-dark-pink hover:text-white;
}
.filled-dark {
  @apply bg-gray-12 hover:bg-gray-11 border-tx text-white hover:text-white disabled:opacity-70;
}
.filled-gray {
  @apply text-gray-12 hover:bg-gray-12 bg-gray-2 border-tx hover:text-white;
}
.filled-white {
  @apply text-gray-12 hover:bg-gray-12 border-tx bg-white hover:text-white;
}
.bordered-white {
  @apply text-gray-12 hover:border-gray-3 border-white bg-white;
}
.bordered-white-pressed {
  @apply bg-gray-12 hover:border-gray-11 hover:bg-gray-11 border-tx text-white hover:focus-visible:border-tx;
}
.bordered-gray {
  @apply text-gray-12 hover:border-gray-12 border-gray-3 bg-white focus-visible:border-tx hover:focus-visible:border-tx;
}
.transparent-tx {
  @apply border-tx;
}
.transparent-gray {
  @apply text-gray-12 hover:bg-gray-12 disabled:text-gray-5 border-tx bg-tx hover:bg-opacity-10;
}
.transparent-dark {
  @apply text-gray-12 hover:bg-gray-12 border-tx bg-tx hover:text-white;
}
.transparent-dark-pressed {
  @apply bg-gray-12 hover:border-gray-11 border-tx text-white;
}

.icon-only {
  @apply flex-none;
}
.small {
  @apply h-8 px-2 py-0;
}
.small.icon-only {
  @apply w-8 p-0;
}
.small.icon-start {
  @apply gap-x-1 ps-1;
}
.small.icon-end {
  @apply gap-x-1 pe-1;
}

.medium {
  @apply h-10 px-3 py-0;
}
.medium.icon-only {
  @apply w-10 p-0;
}
.medium.icon-start {
  @apply gap-x-2 ps-2;
}
.medium.icon-end {
  @apply gap-x-2 pe-2;
}

.large {
  @apply h-12 px-5 py-0;
}
.large.icon-only {
  @apply w-12 p-0;
}
.large.icon-start {
  @apply gap-x-2 ps-4;
}
.large.icon-end {
  @apply gap-x-2 pe-4;
}

.larger {
  @apply h-16;
}
.larger.icon-only {
  @apply w-16;
}
</style>
