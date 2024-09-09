<script setup lang="ts">
/**
 * Renders a radio input field, useful for choosing one of a few options that
 * can all be presented on the screen at once.
 */
import { computed } from "vue"

import VSvg from "~/components/VSvg/VSvg.vue"

defineOptions({ inheritAttrs: false })

const emit = defineEmits<{ "update:modelValue": [string] }>()
const props = withDefaults(
  defineProps<{
    /**
     * The input `id` property. This is used to connect the label to the radio.
     */
    id: string
    /**
     * the value associated with this radio input
     */
    value: string
    /**
     * the value of the `v-model` associated with the radio group
     */
    modelValue?: string
  }>(),
  {
    modelValue: "",
  }
)

const isChecked = computed(() => props.value === props.modelValue)
const handleInput = () => {
  emit("update:modelValue", props.value)
}
</script>

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
      class="radiomark pointer-events-none absolute start-0 h-5 w-5 text-default opacity-0 transition-opacity"
      width="20"
      height="20"
    />
    <!--  @slot Label content goes here  -->
    <slot />
  </label>
</template>

<style scoped>
.radio:checked ~ .radiomark {
  @apply opacity-100;
}

.radio:disabled ~ .radiomark {
  @apply text-secondary;
}
</style>
