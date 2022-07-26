<template>
  <label :for="id" class="radio-label relative flex leading-5">
    <input
      :id="id"
      v-bind="$attrs"
      :value="value"
      class="radio relative h-5 w-5 flex-shrink-0 appearance-none rounded-full border border-dark-charcoal bg-white me-3 focus:outline-none focus:ring focus:ring-pink focus:ring-offset-2 disabled:border-dark-charcoal-40 disabled:bg-dark-charcoal-10"
      type="radio"
      :checked="isChecked"
      @input="handleInput"
    />
    <Radiomark
      class="radiomark absolute h-5 w-5 text-dark-charcoal opacity-0 transition-opacity start-0"
      focusable="false"
      width="20"
      height="20"
      aria-hidden="true"
    />
    <!--  @slot Label content goes here  -->
    <slot />
  </label>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'

import Radiomark from '~/assets/icons/radiomark.svg?inline'

/**
 * Renders a radio input field, useful for choosing one of a few options that
 * can all be presented on the screen at once.
 */
export default {
  name: 'VRadio',
  components: { Radiomark },
  inheritAttrs: false,
  model: {
    prop: 'modelValue',
    event: 'change',
  },
  props: {
    /**
     * the input `id` property; This is used to connect the label to the radio.
     */
    id: {
      type: String,
      required: true,
    },
    /**
     * the value associated with this radio input
     */
    value: {
      type: String,
      required: true,
    },
    /**
     * the value of the `v-model` associated with the radio group
     */
    modelValue: {
      type: String,
      default: '',
    },
  },
  setup(props, { emit }) {
    const isChecked = computed(() => props.value === props.modelValue)
    const handleInput = () => {
      emit('change', props.value)
    }

    return {
      isChecked,
      handleInput,
    }
  },
}
</script>

<style scoped>
.radio:checked ~ .radiomark {
  @apply opacity-100;
}

.radio:disabled ~ .radiomark {
  @apply text-dark-charcoal-70;
}
</style>
