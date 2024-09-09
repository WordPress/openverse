<script setup lang="ts">
/**
 * Provides a control to enter text as input.
 */
import { ref, computed, useAttrs, type InputTypeHTMLAttribute } from "vue"

defineOptions({ inheritAttrs: false })
/**
 * the textual content of the input field
 */
const modelValue = defineModel<string>()
type Connection = "start" | "end"

withDefaults(
  defineProps<{
    /**
     * the textual content of the label associated with this input field; This
     * label is SR-only. If you want to display a visible label, add
     * `for="fieldId"` to the label element and set the `fieldId` prop to the
     * same value as the `for` attribute.
     */
    labelText?: string
    /**
     * the ID to assign to the field; This can be used to attach custom labels
     * to the field.
     */
    fieldId: string
    /**
     * list of sides where the field is connected to other controls
     */
    connectionSides?: Connection[]

    placeholder?: string
    type?: InputTypeHTMLAttribute
  }>(),
  {
    connectionSides: () => [],
    type: "text",
  }
)

const emit = defineEmits<{ "update:modelValue": [string] }>()
const attrs = useAttrs()
const inputEl = ref<HTMLInputElement | null>(null)

const focusInput = () => {
  inputEl.value?.focus()
}

const updateModelValue = (event: Event) => {
  emit("update:modelValue", (event.target as HTMLInputElement).value)
}

const nonClassAttrs = computed(() => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { class: _, ...rest } = attrs
  return rest
})
defineExpose({ focusInput })
</script>

<template>
  <div
    class="input-field group flex h-12 flex-row items-center overflow-hidden rounded-sm border p-0.5px focus-within:border-1.5 focus-within:border-focus focus-within:bg-surface focus-within:p-0 group-hover:bg-surface"
    :class="[
      {
        // Padding is set to 1.5px to accommodate the border that will appear later.
        'rounded-s-none border-s-0 ps-1.5px focus-within:rounded-s-none focus-within:border-s-0 focus-within:ps-1.5px':
          connectionSides.includes('start'),
        'rounded-e-none border-e-0 pe-1.5px focus-within:rounded-e-none focus-within:border-e-0 focus-within:pe-1.5px':
          connectionSides.includes('end'),
      },
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

<style scoped>
.input-field:focus-within .info {
  @apply text-default;
}

.input-field input::placeholder {
  font-weight: normal;
}
</style>
