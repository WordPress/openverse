<template>
  <div
    class="relative m-0.5px box-content block w-fit overflow-hidden rounded-sm border border-dark-charcoal border-opacity-20 text-sm focus-within:m-0 focus-within:border-1.5 focus-within:border-pink hover:border-dark-charcoal focus-within:hover:border-pink"
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
      v-model="modelMedium"
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

<script lang="ts">
import { defineComponent, computed, PropType } from "vue"

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
  NonNullable<(typeof VSelectField)["props"]>
>

/**
 * This field present many viable choices of which any one may be selected.
 */
const VSelectField = defineComponent({
  name: "VSelectField",
  components: { VIcon },
  inheritAttrs: false,
  model: {
    prop: "modelValue",
    event: "update:modelValue",
  },
  props: {
    modelValue: {
      type: String,
      default: "",
    },
    /**
     * the text to associate with the blank value option; Skipping this prop
     * removes the option. This string should be translated.
     */
    blankText: {
      type: String,
    },
    /**
     * the textual content of the label associated with this input field; This
     * label is SR-only and should be translated.
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
     * a list of valid choices for this select field. i18n functionality can be
     * individually toggled for each option
     */
    choices: {
      type: Array as PropType<Choice[]>,
      default: () => [],
    },
  },
  // using non-native event name to ensure the two are not mixed
  emits: {
    "update:modelValue": defineEvent<[string]>(),
  },
  setup(props, { emit, attrs, slots }) {
    const fieldName = computed(() => (attrs["name"] as string) ?? props.fieldId)
    const modelMedium = computed<string>({
      get: () => props.modelValue,
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

    return {
      fieldName,
      modelMedium,
      hasStartContent,
      splitAttrs,
    }
  },
})

export default VSelectField
</script>
