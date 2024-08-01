<template>
  <div
    class="input-field group flex flex-row items-center overflow-hidden rounded-sm border p-0.5px focus-within:border-1.5 focus-within:border-border-focus focus-within:bg-bg-surface focus-within:p-0 group-hover:bg-bg-surface"
    :class="[
      {
        // Padding is set to 1.5px to accommodate the border that will appear later.
        'rounded-s-none border-s-0 ps-1.5px focus-within:rounded-s-none focus-within:border-s-0 focus-within:ps-1.5px':
          connectionSides.includes('start'),
        'rounded-e-none border-e-0 pe-1.5px focus-within:rounded-e-none focus-within:border-e-0 focus-within:pe-1.5px':
          connectionSides.includes('end'),
      },
      sizeClass,
      $attrs.class,
    ]"
  >
    <input
      :id="fieldId"
      v-bind="nonClassAttrs"
      ref="inputEl"
      :placeholder="placeholder"
      :type="type"
      class="ms-4 h-full w-full appearance-none rounded-none bg-tx text-2xl font-semibold leading-none placeholder-gray-8 focus-visible:outline-none md:text-base"
      :value="modelValue"
      :aria-label="labelText"
      @input="updateModelValue"
    />

    <!-- @slot Extra information goes here -->
    <slot />
  </div>
</template>

<script lang="ts">
import {
  ref,
  computed,
  defineComponent,
  PropType,
  InputTypeHTMLAttribute,
} from "vue"

import { defineEvent } from "~/types/emits"

export const FIELD_SIZES = {
  medium: "h-12",
} as const
export type FieldSize = keyof typeof FIELD_SIZES

/**
 * Provides a control to enter text as input.
 */
export default defineComponent({
  name: "VInputField",
  inheritAttrs: false,
  model: {
    prop: "modelValue",
    event: "update:modelValue",
  },
  props: {
    /**
     * the textual content of the input field
     */
    modelValue: {
      type: String,
      default: "",
    },
    /**
     * the textual content of the label associated with this input field; This
     * label is SR-only. If you want to display a visible label, add
     * `for="fieldId"` to the label element and set the `fieldId` prop to the
     * same value as the `for` attribute.
     */
    labelText: {
      type: String,
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
        v.every((item) => ["start", "end"].includes(item)),
    },
    /**
     *  Medium size is for desktop header
     *  Large size is for mobile header
     */
    size: {
      type: String as PropType<keyof typeof FIELD_SIZES>,
      required: true,
      validator: (v: string) => Object.keys(FIELD_SIZES).includes(v),
    },
    placeholder: {
      type: String,
    },
    type: {
      type: String as PropType<InputTypeHTMLAttribute>,
      default: "text",
    },
  },
  emits: {
    "update:modelValue": defineEvent<[string]>(),
  },
  expose: ["focusInput"],
  setup(props, { emit, attrs }) {
    const inputEl = ref<HTMLInputElement | null>(null)

    const focusInput = () => {
      inputEl.value?.focus()
    }

    const updateModelValue = (event: Event) => {
      emit("update:modelValue", (event.target as HTMLInputElement).value)
    }
    const sizeClass = computed(() => FIELD_SIZES[props.size])

    const nonClassAttrs = computed(() => {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { class: _, ...rest } = attrs
      return rest
    })

    return {
      inputEl,

      focusInput,

      emit,

      sizeClass,
      nonClassAttrs,
      updateModelValue,
    }
  },
})
</script>

<style scoped>
.input-field:focus-within .info {
  @apply text-text;
}

.input-field input::placeholder {
  font-weight: normal;
}
</style>
