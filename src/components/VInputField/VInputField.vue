<template>
  <div
    class="input-field group flex flex-row items-center focus-within:bg-dark-charcoal-06 group-hover:bg-dark-charcoal-06 p-0.5px focus-within:p-0 border focus-within:border-1.5 border-dark-charcoal-20 rounded-sm overflow-hidden focus-within:border-pink"
    :class="[
      {
        // Padding is set to 1.5px to accommodate the border that will appear later.
        'border-s-0 ps-1.5px rounded-s-none': connectionSides.includes('start'),
        'border-e-0 pe-1.5px rounded-e-none': connectionSides.includes('end'),
      },
      sizeClass,
    ]"
  >
    <input
      :id="fieldId"
      v-bind="$attrs"
      :type="type"
      class="w-full leading-none font-semibold bg-tx placeholder-dark-charcoal-70 ms-4 h-full appearance-none rounded-none focus:outline-none text-2xl md:text-base"
      :value="modelValue"
      :aria-label="labelText"
      @input="updateModelValue"
      v-on="$listeners"
    />

    <!-- @slot Extra information goes here -->
    <slot />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { defineEvent } from '~/types/emits'

export const FIELD_SIZES = {
  small: 'h-10 text-md',
  medium: 'h-12',
  large: 'h-14',
  standalone: 'h-full',
} as const
export type FieldSize = keyof typeof FIELD_SIZES

/**
 * Provides a control to enter text as input.
 */
export default defineComponent({
  name: 'VInputField',
  inheritAttrs: false,
  model: {
    prop: 'modelValue',
    event: 'update:modelValue',
  },
  props: {
    /**
     * the textual content of the input field
     */
    modelValue: {
      type: String,
      default: '',
    },
    /**
     * the textual content of the label associated with this input field; This
     * label is SR-only.
     */
    labelText: {
      type: String,
      required: true,
    },
    /**
     * the ID to assign to the field; This can be used to attach custom labels
     * to the field.
     */
    fieldId: {
      type: String,
      required: true,
    },
    /**
     * list of sides where the field is connected to other controls
     */
    connectionSides: {
      type: Array,
      default: () => [],
      validator: (v: string[]) =>
        v.every((item) => ['start', 'end'].includes(item)),
    },
    /**
     *  Small size is for mobile header/scrolled
     *  Medium size is for desktop header
     *  Large size is for mobile header/non-scrolled
     *  Standalone size is for homepage
     */
    size: {
      type: String as PropType<keyof typeof FIELD_SIZES>,
      required: true,
      validator: (v: string) => Object.keys(FIELD_SIZES).includes(v),
    },
  },
  // using non-native event name to ensure the two are not mixed
  emits: {
    'update:modelValue': defineEvent<[string]>(),
  },
  setup(props, { emit, attrs }) {
    const type = typeof attrs['type'] === 'string' ? attrs['type'] : 'text'

    const updateModelValue = (event: Event) => {
      emit('update:modelValue', (event.target as HTMLInputElement).value)
    }
    const sizeClass = computed(() => FIELD_SIZES[props.size])

    return {
      emit,
      type,

      sizeClass,
      updateModelValue,
    }
  },
})
</script>

<style scoped>
.input-field:focus-within .info {
  @apply text-dark-charcoal;
}

.input-field input::placeholder {
  font-weight: normal;
}
</style>
