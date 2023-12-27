<template>
  <Component
    :is="as"
    :type="typeAttribute"
    class="group/button flex appearance-none items-center justify-center rounded-sm no-underline"
    :class="[
      $style.button,
      $style[variant],
      $style[`size-${size}${iconOnly ? '-icon-only' : ''}`],
      connectionStyles,
      {
        [$style[`${variant}-pressed`]]: isActive,
        [$style[`icon-start-${size}`]]: hasIconStart,
        [$style[`icon-end-${size}`]]: hasIconEnd,
        [$style[`icon-only`]]: iconOnly,
        'gap-x-2':
          (hasIconEnd || hasIconStart) && (size == 'medium' || size == 'large'),
        'gap-x-1': (hasIconEnd || hasIconStart) && size == 'small',
        // Custom tailwind classes don't work with CSS modules in Vue, so they are
        // written here explicitly instead of accessed off of `$style`.
        'focus-slim-filled': isFocusSlimFilled,
        'focus-slim-tx': isFocusSlimTx,
        'focus-bold-filled ': variant === 'dropdown-label-pressed',
        border: !isPlainDangerous,
      },
    ]"
    :aria-pressed="pressed"
    :aria-disabled="ariaDisabled"
    :disabled="disabledAttribute"
    v-bind="$attrs"
    v-on="$listeners"
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
     * work like another element (like an `anchor`). May only be either `button` or `a`.
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
     *
     * @default false
     */
    pressed: {
      type: Boolean,
      default: false,
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
      props.as === "VLink" ? undefined : props.type
    )

    const connectionStyles = computed(() =>
      props.connections
        .map((connection) => `connection-${connection}`)
        .join(" ")
    )

    const isActive = computed(() => {
      return props.pressed || attrs["aria-pressed"] || attrs["aria-expanded"]
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
        ["dropdown-label", "plain"].includes(props.variant)
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
        if (["a", "NuxtLink"].includes(as)) {
          warn(
            `Please use \`VLink\` with an \`href\` prop instead of ${as} for the button component`
          )
        }
      },
      { immediate: true }
    )

    return {
      disabledAttribute,
      ariaDisabled,
      typeAttribute,
      isActive,
      connectionStyles,
      isPlainDangerous,
      isFocusSlimFilled,
      isFocusSlimTx,
    }
  },
})

export default VButton
</script>

<style module>
.button[disabled="disabled"],
.button[aria-disabled="true"] {
  @apply cursor-not-allowed;
}

.size-small {
  @apply h-8 px-2 py-0;
}
.size-small-icon-only {
  @apply h-8 w-8;
}
.icon-start-small {
  @apply ps-1;
}
.icon-end-small {
  @apply pe-1;
}

.size-medium {
  @apply h-10 px-3 py-0;
}
.size-medium-icon-only {
  @apply h-10 w-10;
}
.icon-start-medium {
  @apply ps-2;
}
.icon-end-medium {
  @apply pe-2;
}

.size-large {
  @apply h-12 px-5 py-0;
}
.size-large-icon-only {
  @apply h-12 w-12;
}
.icon-start-large {
  @apply ps-4;
}
.icon-end-large {
  @apply pe-4;
}

.size-larger-icon-only {
  @apply h-16 w-16;
}

.icon-only {
  @apply flex-none;
}

a.button {
  @apply no-underline hover:no-underline;
}

.filled-pink {
  @apply border-tx bg-pink text-white hover:bg-dark-pink hover:text-white;
}

.filled-dark {
  @apply border-tx bg-dark-charcoal text-white hover:bg-dark-charcoal-90 hover:text-white disabled:opacity-70;
}

.filled-gray {
  @apply border-tx bg-dark-charcoal-10 text-dark-charcoal hover:bg-dark-charcoal hover:text-white;
}

.filled-white {
  @apply border-tx bg-white text-dark-charcoal hover:bg-dark-charcoal hover:text-white;
}

.bordered-white {
  @apply border-white bg-white text-dark-charcoal hover:border-dark-charcoal-20;
}
.bordered-white-pressed {
  @apply border border-tx bg-dark-charcoal text-white hover:border-dark-charcoal-90 hover:bg-dark-charcoal-90;
}

.bordered-gray {
  @apply border-dark-charcoal-20 bg-white text-dark-charcoal hover:border-dark-charcoal;
}

.transparent-tx {
  @apply border-tx;
}
.transparent-gray {
  @apply border-tx bg-tx text-dark-charcoal hover:bg-dark-charcoal hover:bg-opacity-10 disabled:text-dark-charcoal-40;
}
.transparent-dark {
  @apply border-tx bg-tx text-dark-charcoal hover:bg-dark-charcoal hover:text-white;
}
.transparent-dark-pressed {
  @apply border-tx bg-dark-charcoal text-white hover:border-dark-charcoal-90;
}

.dropdown-label {
  @apply border-dark-charcoal-20 bg-white text-dark-charcoal hover:border-tx hover:bg-dark-charcoal hover:text-white;
}
.dropdown-label-pressed {
  @apply border-tx bg-dark-charcoal text-white active:hover:border-white;
}
</style>

<style scoped>
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
</style>
