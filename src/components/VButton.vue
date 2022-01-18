<template>
  <Component
    :is="as"
    :type="typeRef"
    class="transition-colors"
    :class="[
      $style.button,
      $style[variant],
      isActive && $style[`${variant}-pressed`],
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
import {
  defineComponent,
  ref,
  watch,
  toRefs,
  computed,
} from '@nuxtjs/composition-api'
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
      type: /** @type {import('@nuxtjs/composition-api').PropType<'a' | 'button'>} */ (
        String
      ),
      default: 'button',
      validate: (v) => ['a', 'button', 'NuxtLink'].includes(v),
    },
    /**
     * The variant of the button.
     *
     * @default 'primary'
     */
    variant: {
      type: /** @type {import('@nuxtjs/composition-api').PropType<'primary' | 'secondary' | 'tertiary' | 'action-menu' | 'action-menu-muted' | 'grouped'>} */ (
        String
      ),
      default: 'primary',
      validate: (v) =>
        [
          'primary',
          'secondary',
          'tertiary',
          'action-menu',
          'action-menu-secondary',
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
     * The size of the button. `disabled` removes all internal padding allowing
     * the consumer of the component to determine the padding.
     *
     * @default 'medium'
     */
    size: {
      type: /** @type {import('@nuxtjs/composition-api').PropType<'large' | 'medium' | 'small' | 'disabled'>} */ (
        String
      ),
      default: 'medium',
      validate: (v) => ['large', 'medium', 'small', 'disabled'].includes(v),
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
      type: /** @type {import('@nuxtjs/composition-api').PropType<'buton' | 'submit' | 'reset'>} */ (
        String
      ),
      default: 'button',
      validate: (v) => ['button', 'submit', 'reset'].includes(v),
    },
  },
  /**
   * @param {Props} props
   * @param {import('@nuxtjs/composition-api').SetupContext}
   */
  setup(props, { attrs }) {
    const propsRef = toRefs(props)
    const disabledAttributeRef = ref(propsRef.disabled.value)
    const ariaDisabledRef = ref()
    const trulyDisabledRef = ref()
    const typeRef = ref(propsRef.type.value)
    const supportsDisabledAttributeRef = ref(true)

    const isActive = computed(() => {
      return (
        propsRef.pressed.value ||
        attrs['aria-pressed'] ||
        attrs['aria-expanded']
      )
    })
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
        if (['a', 'NuxtLink'].includes(as)) {
          typeRef.value = undefined
          supportsDisabledAttributeRef.value = false
          if (as === 'a') {
            // No need to declare `href` as an explicit prop as Vue preserves
            // the `attrs` object reference between renders and updates the properties
            // meaning we'll always have the latest values for the properties on the
            // attrs object
            if (!attrs.href || attrs.href === '#') {
              warn(
                'Do not use anchor elements without a valid `href` attribute. Use a `button` instead.'
              )
            }
          } else {
            if (!attrs.to) {
              warn('NuxtLink needs a `to` attribute')
            }
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
      isActive,
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
  @apply bg-dark-charcoal-80 hover:border-tx;
}

.tertiary {
  @apply bg-white text-black border border-dark-charcoal-20 focus-visible:border-tx focus-visible:ring-pink ring-offset-0;
}

.tertiary-pressed {
  @apply bg-dark-charcoal text-white border-tx;
}

.action-menu {
  @apply bg-white text-black border border-tx hover:border-dark-charcoal-20 focus-visible:ring-pink;
}

.action-menu-secondary {
  @apply bg-white text-black border border-tx hover:border-dark-charcoal-20 focus-visible:ring-pink;
}

.action-menu-secondary-pressed {
  @apply border-tx bg-dark-charcoal text-white;
}

.action-menu-pressed {
  @apply border-tx hover:border-tx bg-dark-charcoal text-white;
}

.action-menu-muted {
  @apply bg-dark-charcoal-10 text-black border border-tx hover:border-dark-charcoal-20 focus-visible:ring-pink;
}

.action-menu-muted-pressed {
  @apply border-tx bg-dark-charcoal text-white focus-visible:ring-pink;
}

.grouped {
  @apply bg-white text-black focus-visible:ring-pink;
}

.grouped-pressed {
  @apply bg-dark-charcoal-10 ring-offset-dark-charcoal-10;
}

.full {
  @apply w-full font-semibold bg-dark-charcoal-06 focus-visible:ring-pink hover:bg-dark-charcoal-40 hover:text-white;
}

.full-pressed {
  @apply w-full font-semibold bg-dark-charcoal-06 text-dark-charcoal;
}

.plain {
  @apply bg-tx focus-visible:ring-pink;
}
</style>
