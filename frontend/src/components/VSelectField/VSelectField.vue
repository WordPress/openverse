<script setup lang="ts">
import { computed, useAttrs, useSlots } from "vue"

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
    showSelected?: boolean
    /** whether to show a glowing pink outline, indicating a new feature */
    showNewHighlight?: boolean
  }>(),
  {
    modelValue: "",
    blankText: "",
    showSelected: true,
    showHighlight: false,
  }
)

const emit = defineEmits<{ "update:modelValue": [string] }>()

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
  <div class="relative">
    <div
      v-if="showNewHighlight"
      class="new-highlight absolute -inset-1.5px animate-new-highlight rounded-[calc(0.125rem_+_1.5px)]"
      aria-hidden="true"
    ></div>
    <div
      class="relative m-0.5px box-content block w-fit rounded-sm border bg-curr-page text-sm focus-within:m-0 focus-within:border-1.5 focus-within:border-focus hover:border-hover focus-within:hover:border-focus"
      :class="[
        splitAttrs.classAttrs,
        showNewHighlight ? 'border-tx' : 'border-default',
      ]"
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
        class="flex h-[calc(theme(spacing.10)_-_2_*_theme(borderWidth.DEFAULT))] appearance-none truncate bg-tx pe-10"
        :class="[
          showSelected ? 'w-full' : 'w-0 max-w-0',
          hasStartContent ? 'ps-10' : 'ps-2',
        ]"
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
  </div>
</template>

<style>
@property --deg {
  syntax: "<angle>";
  initial-value: 0deg;
  inherits: false;
}

.new-highlight {
  background: linear-gradient(
    var(--deg),
    var(--color-gray-new-highlight),
    var(--color-new-highlight)
  );
}
</style>
