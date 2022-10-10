<template>
  <VButton
    v-bind="buttonProps"
    size="disabled"
    class="icon-button flex flex-shrink-0 items-center justify-center border-1.5 active:shadow-ring"
    :class="buttonSizeClasses"
    :type="type"
    v-on="$listeners"
  >
    <slot name="default" :icon-size-classes="iconSizeClasses" />
    <VIcon
      v-if="iconProps"
      class="pointer-events-none"
      :class="iconSizeClasses"
      v-bind="iconProps"
    />
  </VButton>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { ButtonType } from '~/types/button'

import VIcon, { type IconProps } from '~/components/VIcon/VIcon.vue'
import VButton, { type ButtonProps } from '~/components/VButton.vue'

const SIZE_MAP = Object.freeze({
  tiny: { icon: 'w-6 h-6', button: 'w-6 h-6' },
  small: { icon: 'w-6 h-6', button: 'w-10 h-10' },
  smaller: { icon: 'w-6 h-6', button: 'w-8 h-8' },
  // TODO: audit the sizes after new header is done.
  'new-small': { icon: 'w-4 h-4', button: 'w-8 h-8' },
  'search-small': {
    icon: 'w-6 h-6',
    button: 'w-10 md:w-12 h-10 md:h-12',
  },
  'search-medium': { icon: 'w-6 h-6', button: 'w-12 h-12' },
  'search-large': { icon: 'w-6 h-6', button: 'w-14 h-14' },
  'search-standalone': {
    icon: 'w-6 h-6',
    button: 'w-14 md:w-[69px] h-14 md:h-[69px]',
  },
  medium: { icon: 'w-8 h-8', button: 'w-14 h-14' },
  large: { icon: 'w-12 h-12', button: 'w-20 h-20' },
} as const)
type Size = keyof typeof SIZE_MAP

export default defineComponent({
  name: 'VIconButton',
  components: { VIcon, VButton },
  props: {
    /**
     * the size of the button; The size affects both the size of the button
     * itself and the icon inside it.
     */
    size: {
      type: String as PropType<Size>,
      default: 'medium',
      validator: (val: string) => Object.keys(SIZE_MAP).includes(val),
    },
    /**
     * props to pass down to the `VIcon` component nested inside the button; See
     * documentation on `VIcon`.
     */
    iconProps: {
      type: Object as PropType<IconProps>,
      required: false,
    },
    /**
     * props to pass down to the `VButton` component nested inside the button;
     * See documentation on `VButton`.
     */
    buttonProps: {
      type: Object as PropType<ButtonProps>,
      default: () => ({ variant: 'plain' }),
    },
  },
  setup(props, { attrs }) {
    const type = (attrs['type'] ?? 'button') as ButtonType

    const buttonSizeClasses = computed(() => SIZE_MAP[props.size].button)
    const iconSizeClasses = computed(() => SIZE_MAP[props.size].icon)

    return {
      type,

      buttonSizeClasses,
      iconSizeClasses,
    }
  },
})
</script>
