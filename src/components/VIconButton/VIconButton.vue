<template>
  <button
    class="icon-button flex items-center justify-center border-1.5 focus:border-pink focus:outline-none focus:shadow-ring active:shadow-ring"
    :class="[...buttonSizeClasses]"
    :type="type"
    v-on="$listeners"
  >
    <VIcon
      class="pointer-events-none"
      :class="[...iconSizeClasses]"
      v-bind="iconProps"
    />
  </button>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'

import VIcon from '~/components/VIcon/VIcon.vue'

export default {
  name: 'VIconButton',
  components: { VIcon },
  props: {
    /**
     * the size of the button; The size affects both the size of the button
     * itself and the icon inside it.
     */
    size: {
      type: String,
      default: 'medium',
      validator: (val) =>
        ['tiny', 'small', 'search', 'medium', 'large'].includes(val),
    },
    /**
     * props to pass down to the `VIcon` component nested inside the button; See
     * documentation on `VIcon`.
     */
    iconProps: {},
  },
  setup(props, { attrs }) {
    const type = attrs['type'] ?? 'button'

    const buttonSizeClasses = computed(
      () =>
        ({
          tiny: ['w-6', 'h-6'],
          small: ['w-10', 'h-10'],
          search: ['w-12', 'h-12'],
          medium: ['w-14', 'h-14'],
          large: ['w-20', 'h-20'],
        }[props.size])
    )
    const iconSizeClasses = computed(
      () =>
        ({
          tiny: ['w-6', 'h-6'],
          small: ['w-6', 'h-6'],
          search: ['w-6', 'h-6'],
          medium: ['w-8', 'h-8'],
          large: ['w-12', 'h-12'],
        }[props.size])
    )

    return {
      type,

      buttonSizeClasses,
      iconSizeClasses,
    }
  },
}
</script>
