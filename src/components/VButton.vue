<template>
  <Component
    :is="as"
    :type="typeRef"
    class="flex appearance-none items-center justify-center rounded-sm no-underline ring-offset-1 transition-shadow duration-100 ease-linear focus:outline-none"
    :class="[
      $style.button,
      $style[variant],
      isConnected && $style[`connection-${connections}`],
      isActive && $style[`${variant}-pressed`],
      $style[`size-${size}`],
      isPlainDangerous
        ? ''
        : 'border border-tx focus-visible:ring focus-visible:ring-pink',
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

<script lang="ts">
import {
  defineComponent,
  ref,
  watch,
  toRefs,
  computed,
  PropType,
} from '@nuxtjs/composition-api'

import { warn } from '~/utils/console'

import type { ProperlyExtractPropTypes } from '~/types/prop-extraction'
import {
  ButtonConnections,
  buttonForms,
  ButtonSize,
  ButtonType,
  ButtonVariant,
} from '~/types/button'
import type { ButtonForm } from '~/types/button'

import VLink from '~/components/VLink.vue'

export type ButtonProps = ProperlyExtractPropTypes<
  NonNullable<typeof VButton['props']>
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
  name: 'VButton',
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
      default: 'button',
      validate: (val: ButtonForm) => buttonForms.includes(val),
    },
    /**
     * The variant of the button.
     *
     * Plain removes all styles except the focus ring.
     * Plain--avoid removes _all_ styles including the focus ring.
     *
     * @default 'primary'
     */
    variant: {
      type: String as PropType<ButtonVariant>,
      default: 'primary',
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
      default: 'medium',
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
      default: 'button',
    },
    /**
     * Whether the button is connected to another control and needs to have no rounded
     * borders at that edge.
     * `all` means that the button is not rounded.
     *
     * @default 'none'
     */
    connections: {
      type: String as PropType<ButtonConnections>,
      default: 'none',
    },
  },
  setup(props, { attrs }) {
    const propsRef = toRefs(props)
    const disabledAttributeRef = ref<boolean | undefined>(
      propsRef.disabled.value
    )
    const ariaDisabledRef = ref<boolean>()
    const trulyDisabledRef = ref<boolean>()
    const typeRef = ref<ButtonType | undefined>(propsRef.type.value)
    const supportsDisabledAttributeRef = ref(true)

    const isConnected = computed(() => props.connections !== 'none')

    const isActive = computed(() => {
      return (
        propsRef.pressed.value ||
        attrs['aria-pressed'] ||
        attrs['aria-expanded']
      )
    })

    const isPlainDangerous = computed(() => {
      return propsRef.variant.value === 'plain--avoid'
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
        if (['VLink'].includes(as)) {
          typeRef.value = undefined
          supportsDisabledAttributeRef.value = false
        } else if (['a', 'NuxtLink'].includes(as)) {
          warn(
            `Please use \`VLink\` with an \`href\` prop instead of ${as} for the button component`
          )
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
      isConnected,
      isPlainDangerous,
    }
  },
})

export default VButton
</script>

<style module>
.button[disabled='disabled'],
.button[aria-disabled='true'] {
  @apply cursor-not-allowed;
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
  @apply no-underline hover:no-underline;
}

.primary {
  @apply border-tx bg-pink text-white hover:border-tx hover:bg-dark-pink hover:text-white;
}
.primary-pressed {
  @apply bg-dark-pink;
}

.secondary {
  @apply border-tx bg-tx hover:bg-dark-charcoal hover:text-white focus-visible:ring focus-visible:ring-pink;
}
.secondary-pressed {
  @apply border-tx bg-dark-charcoal text-white hover:border-tx hover:bg-dark-charcoal-90;
}
.secondary[disabled='disabled'],
.secondary[aria-disabled='true'] {
  @apply border-tx bg-tx text-dark-charcoal-40;
}

.secondary-filled {
  @apply border-tx bg-dark-charcoal text-white hover:bg-dark-charcoal-80 hover:text-white focus-visible:ring focus-visible:ring-pink disabled:bg-dark-charcoal-10 disabled:text-dark-charcoal-40;
}

.secondary-bordered {
  @apply border-dark-charcoal bg-tx hover:bg-dark-charcoal hover:text-white focus-visible:border-tx disabled:bg-dark-charcoal-10 disabled:text-dark-charcoal-40;
}
.secondary-bordered-pressed {
  @apply bg-dark-charcoal text-white hover:border-tx hover:bg-dark-charcoal-90 focus-visible:bg-dark-charcoal-90;
}
.secondary-filled[disabled='disabled'],
.secondary-bordered[disabled='disabled'],
.secondary-filled[aria-disabled='true'],
.secondary-bordered[aria-disabled='true'] {
  @apply border-tx bg-dark-charcoal-10 text-dark-charcoal-40;
}

.text {
  @apply border-tx bg-tx px-0 text-sm font-semibold text-pink hover:underline focus-visible:ring focus-visible:ring-pink;
}

.text[disabled='disabled'],
.text[aria-disabled='true'] {
  @apply border-tx bg-tx text-dark-charcoal-40;
}

.menu {
  @apply border-tx bg-white text-dark-charcoal ring-offset-0;
}
.menu-pressed {
  @apply border-tx bg-dark-charcoal text-white;
}

.action-menu {
  @apply border-tx bg-tx text-dark-charcoal hover:border-dark-charcoal-20;
}
.action-menu-pressed {
  @apply border-tx bg-dark-charcoal text-white hover:border-tx hover:bg-dark-charcoal-90;
}

/**
Similar to `action-menu`, but always has a border, not only on hover.
https://www.figma.com/file/GIIQ4sDbaToCfFQyKMvzr8/Openverse-Design-Library?node-id=1684%3A3678
 */
.action-menu-bordered {
  @apply border-dark-charcoal-20 bg-white text-dark-charcoal focus-visible:border-tx;
}
.action-menu-bordered-pressed {
  @apply border-dark-charcoal bg-dark-charcoal text-white hover:bg-dark-charcoal-90;
}

.action-menu-muted {
  @apply border-tx bg-dark-charcoal-10 text-dark-charcoal hover:border-dark-charcoal-20;
}
.action-menu-muted-pressed {
  @apply border-tx bg-dark-charcoal text-white hover:border-tx hover:bg-dark-charcoal-90;
}

.action-menu[disabled='disabled'],
.action-menu[aria-disabled='true'],
.action-menu-muted[disabled='disabled'],
.action-menu-muted[aria-disabled='true'],
.action-menu-bordered[disabled='disabled'],
.action-menu-bordered[aria-disabled='true'] {
  @apply border-dark-charcoal-10 bg-dark-charcoal-10 text-dark-charcoal-40;
}

.action-menu-secondary {
  @apply border border-tx bg-white text-dark-charcoal hover:border-dark-charcoal-20;
}

.action-menu-secondary-pressed {
  @apply border-tx bg-dark-charcoal text-white;
}

.full {
  @apply w-full bg-dark-charcoal-06 font-semibold hover:bg-dark-charcoal-40 hover:text-white;
}

.full-pressed {
  @apply w-full bg-dark-charcoal-06 font-semibold text-dark-charcoal;
}

.connection-start {
  @apply rounded-s-none;
}
.connection-end {
  @apply rounded-e-none;
}
.connection-all {
  @apply rounded-none;
}
</style>
