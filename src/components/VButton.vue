<template>
  <Component
    :is="as"
    :type="typeRef"
    :class="[
      $style.button,
      $style[variant],
      pressed && $style[`${variant}-pressed`],
      $style[`size-${size}`],
    ]"
    :aria-pressed="pressed"
    :aria-disabled="ariaDisabledRef"
    :disabled="disabledAttributeRef"
    v-bind="$attrs"
    v-on="$listeners"
  >
    <!--
      @slot The content of the button
    -->
    <slot />
  </Component>
</template>

<script>
import { defineComponent, ref, watch, toRefs } from '@nuxtjs/composition-api'
import { warn } from '~/utils/warn'

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
  name: 'VButton',
  props: {
    /**
     * Passed to `component :is` to allow the button to *appear* as a button but
     * work like another element (like an `anchor`). May only be either `button` or `a`.
     *
     * We do not support other elements because their use cases are marginal and they
     * add complexity that we can avoid otherwise.
     *
     * We also don't allow any old Vue component because Vue does not have ref-forwarding
     * so we wouldn't be able to detect the type of the DOM node that is ultimately rendered
     * by any Vue component passed.
     *
     * @default 'button'
     */
    as: {
      type: String,
      default: 'button',
      validate: (v) => ['a', 'button'].includes(v),
    },
    /**
     * The variant of the button.
     *
     * @default 'primary'
     */
    variant: {
      type: String,
      default: 'primary',
      validate: (v) =>
        [
          'primary',
          'secondary',
          'tertiary',
          'action-menu',
          'action-menu-muted',
          'grouped',
        ].includes(v),
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
     * The size of the button.
     *
     * @default 'medium'
     */
    size: {
      type: String,
      default: 'medium',
      validate: (v) => ['large', 'medium', 'small'].includes(v),
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
      type: String,
      default: 'button',
      validate: (v) => ['button', 'submit', 'reset'].includes(v),
    },
  },
  /* eslint-disable no-unused-vars */
  setup(props, { attrs }) {
    const propsRef = toRefs(props)
    const disabledAttributeRef = ref(propsRef.disabled.value)
    const ariaDisabledRef = ref()
    const trulyDisabledRef = ref()
    const typeRef = ref(propsRef.type.value)
    const supportsDisabledAttributeRef = ref(true)

    watch(
      [propsRef.disabled, propsRef.focusableWhenDisabled],
      ([disabled, focusableWhenDisabled]) => {
        trulyDisabledRef.value = disabled && !focusableWhenDisabled

        // If disabled and focusable then use `aria-disabled` instead of the `disabled` attribute to allow
        // the button to still be tabbed into by screen reader users
        if (disabled && focusableWhenDisabled) {
          ariaDisabledRef.value = true
        } else {
          ariaDisabledRef.value = undefined
        }
      },
      { immediate: true }
    )

    watch(
      propsRef.as,
      (as) => {
        if (as === 'a') {
          typeRef.value = undefined
          supportsDisabledAttributeRef.value = false

          // No need to decalare `href` as an explicit prop as Vue preserves
          // the `attrs` object reference between renders and updates the properties
          // meaning we'll always have the latest values for the properties on the
          // attrs object
          if (!attrs.href || attrs.href === '#') {
            warn(
              'Do not use anchor elements without a valid `href` attribute. Use a `button` instead.'
            )
          }
        }
      },
      { immediate: true }
    )

    watch(
      [trulyDisabledRef, supportsDisabledAttributeRef],
      ([trulyDisabled, supportsDisabled]) => {
        disabledAttributeRef.value =
          trulyDisabled && supportsDisabled ? true : undefined
      },
      { immediate: true }
    )

    return {
      disabledAttributeRef,
      ariaDisabledRef,
      typeRef,
    }
  },
})

export default VButton
</script>

<style module>
.button {
  @apply flex items-center rounded-sm justify-center transition-shadow duration-100 ease-linear disabled:opacity-70 focus:outline-none focus-visible:ring no-underline appearance-none ring-offset-1;
}

.button[disabled='disabled'],
.button[aria-disabled='true'] {
  @apply opacity-50;
}

.size-small {
  @apply py-1 px-2;
}

.size-medium {
  @apply py-2 px-4;
}

.size-large {
  @apply py-6 px-8;
}

a.button {
  @apply no-underline;
}

.primary {
  @apply bg-pink text-white focus-visible:ring-pink hover:bg-dark-pink hover:text-white;
}

.primary-pressed {
  @apply bg-dark-pink;
}

.secondary {
  @apply bg-dark-charcoal text-white font-bold focus-visible:ring-pink hover:bg-dark-charcoal-80 hover:text-white;
}

.secondary-pressed {
  @apply bg-dark-charcoal-80;
}

.tertiary {
  @apply bg-white text-black hover:bg-dark-charcoal hover:text-white border border-dark-charcoal-20 hover:border-tx focus-visible:ring-pink ring-offset-0;
}

.tertiary-pressed {
  @apply bg-dark-charcoal text-white border-tx;
}

.action-menu {
  @apply bg-white text-black border border-tx hover:border-dark-charcoal-20 focus-visible:ring-pink;
}

.action-menu-pressed {
  @apply border-tx bg-dark-charcoal text-white;
}

.action-menu-muted {
  @apply bg-dark-charcoal-10 text-black border border-tx hover:border-dark-charcoal-20 focus-visible:ring-pink;
}

.action-menu-muted-pressed {
  @apply border-tx bg-dark-charcoal text-white;
}

.grouped {
  @apply bg-white text-black focus-visible:ring-pink;
}

.grouped-pressed {
  @apply bg-dark-charcoal-10 ring-offset-dark-charcoal-10;
}
</style>
