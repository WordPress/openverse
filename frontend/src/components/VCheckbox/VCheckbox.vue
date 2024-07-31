<template>
  <label
    :for="id"
    class="relative flex text-sm leading-5"
    :class="labelClasses"
  >
    <span class="relative block">
      <!--
      The checkbox focus style is a slight variation on the `focus-slim-tx` style.
      Because it becomes filled when checked, it also needs the
      `checked:focus-visible:border-border-bg-ring` class.
      -->
      <input
        :id="id"
        type="checkbox"
        class="border-border-tertiary checked:bg-bg-fill-tertiary disabled:bg-bg-fill-secondary disabled:border-border-disabled checked:disabled:border-border-disabled checked:disabled:bg-bg-fill-disabled me-3 block appearance-none border bg-bg transition-colors duration-100"
        :class="
          isSwitch
            ? ['h-4.5', 'w-9', 'rounded-full', 'focus-slim-offset']
            : [
                'h-5',
                'w-5',
                'rounded-sm',
                'focus-slim-tx',
                'checked:focus-visible:border-border-bg-ring',
              ]
        "
        v-bind="inputAttrs"
        :disabled="disabled ? true : undefined"
        @click="onChange"
      />

      <!-- Knob, for when `ifSwitch` is `true` -->
      <span
        v-if="isSwitch"
        class="absolute left-0.75 top-0.75 block h-3 w-3 rounded-full transition-transform duration-100"
        :class="
          localCheckedState
            ? ['bg-bg', 'translate-x-[1.125rem]']
            : disabled
              ? ['bg-bg-fill-disabled']
              : ['bg-bg-fill-tertiary']
        "
        aria-hidden="true"
      />

      <!-- Checkmark, for when `ifSwitch` is `false` -->
      <VIcon
        v-else
        v-show="localCheckedState"
        class="pointer-events-none absolute inset-0 transform text-text-over-dark"
        name="check"
        :size="5"
      />
    </span>

    <!--  @slot The checkbox label  --><slot />
  </label>
</template>

<script lang="ts">
import { computed, defineComponent, ref, watch } from "vue"

import { defineEvent } from "~/types/emits"

import VIcon from "~/components/VIcon/VIcon.vue"

export type CheckboxAttrs = {
  name: string
  value: string
  disabled?: "disabled" | undefined
  checked?: boolean
}

/**
 * A checkbox input component that allows selection of multiple options from a list .
 *
 * Unlike the native checkbox, this component only has two states: checked / not checked.
 */
export default defineComponent({
  name: "VCheckbox",
  components: {
    VIcon,
  },
  props: {
    /**
     * Checkbox `id` is used for the input id property, connecting the label to
     * the checkbox. id is also used in the `change` event payload as the `name`
     * and `value` parameters if they are not set.
     */
    id: {
      type: String,
      required: true,
    },
    /**
     * Whether the checkbox is checked or not. No indeterminate state is allowed.
     *
     * @default false
     */
    checked: {
      type: Boolean,
      default: false,
    },
    /**
     * Usually this is the category that this checkbox belongs to, e.g. 'license' for a
     * 'by-nc-nd' checkbox, or 'licenseType' for 'commercial' checkbox.
     * This parameter is used in the emitted object.
     *
     * If the form submission is done natively, the name and value parameters are used
     * when sending the form data to the server on form submit: if a checkbox is checked,
     * `name=value` pair is added to the POST request body.
     *
     * If not set, the value of `id` prop is used instead.
     */
    name: {
      type: String,
      required: false,
    },
    /**
     * The value parameter in `name=value` pair sent in the POST request body, here
     * emitted in the event's payload. Usually the code as 'by-nc-nd'.
     *
     * If not set, the value of `id` prop is used.
     */
    value: {
      type: String,
      required: false,
    },
    /**
     * Sets disabled property of the input and changes label opacity if set to true.
     */
    disabled: {
      type: Boolean,
      default: undefined,
    },
    /**
     * whether to make the checkbox appear like a switch
     */
    isSwitch: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    change: defineEvent<[Omit<CheckboxAttrs, "disabled">]>(),
  },
  setup(props, { emit }) {
    const localCheckedState = ref(props.checked || false)
    const labelClasses = computed(() =>
      props.disabled ? "text-text-disabled" : "text-text"
    )
    const inputAttrs = computed<CheckboxAttrs>(() => {
      const attrs: CheckboxAttrs = {
        name: props.name || props.id,
        value: props.value || props.id,
      }
      if (localCheckedState.value) {
        attrs.checked = true
      }
      return attrs
    })

    watch(
      () => props.checked,
      (checked) => {
        if (checked !== localCheckedState.value) {
          localCheckedState.value = checked
        }
      }
    )

    const onChange = () => {
      localCheckedState.value = !localCheckedState.value
      emit("change", {
        name: inputAttrs.value.name,
        value: inputAttrs.value.value,
        checked: localCheckedState.value,
      })
    }
    return {
      localCheckedState,
      labelClasses,
      inputAttrs,
      onChange,
    }
  },
})
</script>
