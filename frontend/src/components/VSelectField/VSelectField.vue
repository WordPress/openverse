<script setup lang="ts">
import { computed, useAttrs, useSlots } from "vue"

import { defineEvent } from "~/types/emits"
import type { ProperlyExtractPropTypes } from "~/types/prop-extraction"

import VIcon from "~/components/VIcon/VIcon.vue"

/**
 * Represents a singular valid option of the dropdown.
 */
export interface Choice {
  /** the programmatic value of this option */
  key: string
  /** the text to show to the user corresponding to this option */
  text: string
}

export type SelectFieldProps = ProperlyExtractPropTypes<
  NonNullable<typeof props>
>

defineOptions({
  inheritAttrs: false,
})
/**
 * This field present many viable choices of which any one may be selected.
 */

const props = withDefaults(
  defineProps<{
    modelValue?: string
    blankText?: string
    fieldId: string
    labelText: string
    choices: Choice[]
  }>(),
  {
    modelValue: "",
    blankText: "",
  }
)

const emit = defineEmits({
  "update:modelValue": defineEvent<[string]>(),
})

const attrs = useAttrs()
const slots = useSlots()

const fieldName = computed(() => (attrs["name"] as string) ?? props.fieldId)
const selectValue = computed<string>({
  get: () => {
    return props.modelValue
  },
  set: (value: string) => {
    emit("update:modelValue", value)
  },
})

const hasStartContent = computed(() => {
  return slots && slots.start && slots.start().length !== 0
})

const splitAttrs = computed(() => {
  const { class: classAttrs, ...rest } = attrs
  return {
    classAttrs,
    nonClassAttrs: rest,
  }
})
</script>

<template>
  <div
    class="relative m-0.5px box-content block w-fit overflow-hidden rounded-sm border border-default text-sm focus-within:m-0 focus-within:border-1.5 focus-within:border-focus hover:border-hover focus-within:hover:border-focus"
    :class="splitAttrs.classAttrs"
  >
    <div class="pointer-events-none absolute inset-y-0 start-2 my-auto h-fit">
      <slot name="start" />
    </div>
    <div class="pointer-events-none absolute inset-y-0 end-2 my-auto h-fit">
      <VIcon name="caret-down" />
    </div>
    <select
      :id="fieldId"
      v-model="selectValue"
      class="flex h-[calc(theme(spacing.10)_-_2_*_theme(borderWidth.DEFAULT))] w-full appearance-none truncate bg-tx pe-10"
      :class="hasStartContent ? 'ps-10' : 'ps-2'"
      :name="fieldName"
      v-bind="splitAttrs.nonClassAttrs"
      :aria-label="labelText"
    >
      <option v-if="blankText" disabled value="">{{ blankText }}</option>
      <option v-for="choice in choices" :key="choice.key" :value="choice.key">
        {{ choice.text }}
      </option>
    </select>
  </div>
</template>
