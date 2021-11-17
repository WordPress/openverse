<template>
  <div
    class="input-field group flex flex-row items-center gap-4 hover:bg-dark-charcoal-06 focus-within:bg-dark-charcoal-06 group-hover:bg-dark-charcoal-06 h-12 p-0.5px focus-within:p-0 border focus-within:border-1.5 border-dark-charcoal-20 rounded-sm overflow-hidden focus-within:border-pink"
    :class="[
      {
        // Padding is set to 1.5px to accommodate the border that will appear later.
        'border-s-0 ps-1.5px rounded-s-none': connectionSides.includes('start'),
        'border-e-0 pe-1.5px rounded-e-none': connectionSides.includes('end'),
      },
    ]"
  >
    <label class="sr-only" :for="fieldId">{{ labelText }}</label>
    <input
      :id="fieldId"
      v-model="text"
      v-bind="$attrs"
      :type="type"
      class="flex-grow leading-none font-semibold bg-tx placeholder-dark-charcoal-70 ms-4 h-full focus:outline-none"
      v-on="$listeners"
    />
    <div
      class="info font-semibold text-xs text-dark-charcoal-70 group-hover:text-dark-charcoal group-focus:text-dark-charcoal me-4"
    >
      <!-- @slot Extra information goes here -->
      <slot />
    </div>
  </div>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'

/**
 * Provides a control to enter text as input.
 */
export default {
  name: 'InputField',
  inheritAttrs: false,
  model: {
    prop: 'value',
    event: 'input',
  },
  props: {
    /**
     * the textual content of the input field
     */
    value: {
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
      validator: (val) => val.every((item) => ['start', 'end'].includes(item)),
    },
  },
  setup(props, { emit, attrs }) {
    const type = attrs['type'] ?? 'text'

    const text = computed({
      get() {
        return props.value
      },
      set(value) {
        emit('input', value)
      },
    })

    return {
      type,

      text,
    }
  },
}
</script>

<style scoped>
.input-field:focus-within .info {
  @apply text-dark-charcoal;
}
</style>
