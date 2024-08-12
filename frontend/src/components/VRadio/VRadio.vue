<template>
  <label :for="id" class="radio-label relative flex leading-5">
    <input
      :id="id"
      v-bind="$attrs"
      :value="value"
      class="radio focus-visible:ring-border-focus relative me-3 h-5 w-5 flex-shrink-0 appearance-none rounded-full border border-tertiary bg-default focus-visible:outline-none focus-visible:ring focus-visible:ring-offset-2 disabled:border-disabled disabled:bg-secondary"
      type="radio"
      :checked="isChecked"
      @input="handleInput"
    />
    <VSvg
      name="radiomark"
      class="radiomark absolute start-0 h-5 w-5 text-default opacity-0 transition-opacity"
      width="20"
      height="20"
    />
    <!--  @slot Label content goes here  -->
    <slot />
  </label>
</template>

<script lang="ts">
import { computed, defineComponent } from "vue"

import { defineEvent } from "~/types/emits"

import VSvg from "~/components/VSvg/VSvg.vue"
/**
 * Renders a radio input field, useful for choosing one of a few options that
 * can all be presented on the screen at once.
 */
export default defineComponent({
  name: "VRadio",
  components: { VSvg },
  inheritAttrs: false,
  model: {
    prop: "modelValue",
    event: "change",
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
      default: "",
    },
  },
  emits: {
    "update:modelValue": defineEvent<[string]>(),
  },
  setup(props, { emit }) {
    const isChecked = computed(() => props.value === props.modelValue)
    const handleInput = () => {
      emit("update:modelValue", props.value)
    }

    return {
      isChecked,
      handleInput,
    }
  },
})
</script>

<style scoped>
.radio:checked ~ .radiomark {
  @apply opacity-100;
}

.radio:disabled ~ .radiomark {
  @apply text-secondary;
}
</style>
