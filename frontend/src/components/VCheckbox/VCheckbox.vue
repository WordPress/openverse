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
      `checked:focus-visible:border-white` class.
      -->
      <input
        :id="id"
        type="checkbox"
        class="block appearance-none border border-dark-charcoal bg-white transition-colors duration-100 me-3 checked:bg-dark-charcoal disabled:border-dark-charcoal-40 disabled:bg-dark-charcoal-10 checked:disabled:border-dark-charcoal-40 checked:disabled:bg-dark-charcoal-40"
        :class="
          isSwitch
            ? ['h-4.5', 'w-9', 'rounded-full', 'focus-slim-offset']
            : [
                'h-5',
                'w-5',
                'rounded-sm',
                'focus-slim-tx',
                'checked:focus-visible:border-white',
              ]
        "
        v-bind="inputAttrs"
        @click="onChange"
      />

      <!-- Knob, for when `ifSwitch` is `true` -->
      <span
        v-if="isSwitch"
        class="absolute top-0.75 left-0.75 block h-3 w-3 rounded-full transition-transform duration-100"
        :class="
          localCheckedState
            ? ['bg-white', 'translate-x-[1.125rem]']
            : disabled
            ? ['bg-dark-charcoal-40']
            : ['bg-dark-charcoal']
        "
        aria-hidden="true"
      />

      <!-- Checkmark, for when `ifSwitch` is `false` -->
      <svg
        v-else
        v-show="localCheckedState"
        class="absolute inset-0 h-5 w-5 flex-shrink-0 flex-grow-0 transform text-white"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        aria-hidden="true"
        focusable="false"
      >
        <g id="icon">
          <path
            d="M17.9293 7.97825L10.731 17.6591L6.21469 14.3009L7.10972 13.0972L10.4223 15.5603L16.7255 7.08322L17.9293 7.97825Z"
            fill="currentColor"
          />
        </g>
      </svg>
    </span>

    <!--  @slot The checkbox label  --><slot />
  </label>
</template>

<script lang="ts">
import { computed, defineComponent, ref, watch } from "vue"

import { defineEvent } from "~/types/emits"

type CheckboxAttrs = {
  name: string
  value: string
  disabled?: boolean
  checked?: boolean
}

/**
 * A checkbox input component that allows selection of multiple options from a list .
 *
 * Unlike the native checkbox, this component only has two states: checked / not checked.
 */
export default defineComponent({
  name: "VCheckbox",
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
      default: false,
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
      props.disabled ? "text-dark-charcoal-70" : "text-dark-charcoal"
    )
    const inputAttrs = computed<CheckboxAttrs>(() => {
      const attrs: CheckboxAttrs = {
        name: props.name || props.id,
        value: props.value || props.id,
      }
      if (props.disabled) {
        attrs.disabled = true
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
