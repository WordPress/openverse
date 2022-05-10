<template>
  <label :for="id" class="checkbox-label" :class="labelClasses">
    <input
      :id="id"
      type="checkbox"
      class="checkbox bg-white"
      v-bind="inputAttrs"
      @change="onChange"
    />
    <VIcon
      v-show="localCheckedState"
      class="absolute start-0 text-white"
      :icon-path="checkmark"
      view-box="0 0 20 20"
      :size="5"
    />
    <!--  @slot The checkbox label  --><slot />
  </label>
</template>

<script lang="ts">
import { computed, defineComponent, ref, watch } from '@nuxtjs/composition-api'

import { defineEvent } from '~/types/emits'

import VIcon from '~/components/VIcon/VIcon.vue'

import checkmark from '~/assets/icons/checkmark.svg'

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
  name: 'VCheckbox',
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
      default: false,
    },
  },
  emits: {
    change: defineEvent<[Omit<CheckboxAttrs, 'disabled'>]>(),
  },
  setup(props, { emit }) {
    const localCheckedState = ref(props.checked || false)
    const labelClasses = computed(() =>
      props.disabled ? 'text-dark-charcoal-70' : 'text-dark-charcoal'
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
      emit('change', {
        name: inputAttrs.value.name,
        value: inputAttrs.value.value,
        checked: localCheckedState.value,
      })
    }
    return {
      checkmark,
      localCheckedState,
      labelClasses,
      inputAttrs,
      onChange,
    }
  },
})
</script>
<style scoped>
.checkbox-label {
  @apply relative flex text-sm leading-5;
}
.checkbox {
  @apply appearance-none w-5 h-5 border-dark-charcoal border rounded-sm me-3 flex-shrink-0 relative;
  @apply focus:outline-none focus:ring focus:ring-offset-2 focus:ring-pink;
  @apply disabled:bg-dark-charcoal-10 disabled:border-dark-charcoal-40;
  @apply checked:bg-dark-charcoal;
  @apply checked:disabled:bg-dark-charcoal-40;
}
</style>
