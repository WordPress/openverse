<template>
  <label :for="id" class="checkbox-label" :class="labelClasses">
    <input
      :id="id"
      type="checkbox"
      class="checkbox"
      v-bind="inputAttrs"
      @change="onChange"
    />
    <Checkmark
      v-show="localCheckedState"
      class="checkmark"
      focusable="false"
      width="20"
      height="20"
      role="img"
    />
    <!--  @slot The checkbox label  --><slot />
  </label>
</template>

<script>
import Checkmark from '~/assets/icons/checkmark.svg?inline'
import { computed, defineComponent, ref, watch } from '@nuxtjs/composition-api'

const VCheckbox = defineComponent({
  name: 'VCheckbox',
  components: { Checkmark },
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
     * The name and value parameters are used when sending the form data to the server
     * using HTML on form submit: if a checkbox is checked, `name=value` pair in
     * the POST request body.
     * In a Vue app, this is used as the name parameter in the emitted event's payload.
     * It is usually the category that this checkbox belongs to, eg. licenseType for a
     * 'by-nc-nd' checkbox.
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
     *
     * @default false
     */
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, { emit }) {
    const localCheckedState = ref(props.checked || false)
    const labelClasses = computed(() =>
      props.disabled ? 'text-dark-charcoal-70' : 'text-dark-charcoal'
    )
    const inputAttrs = computed(() => {
      const attrs = {
        name: props.name || props.id,
        value: props.value || props.id,
      }
      if (props.disabled) {
        attrs.disabled = 'disabled'
      }
      if (localCheckedState.value) {
        attrs.checked = 'checked'
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
      localCheckedState,
      labelClasses,
      inputAttrs,
      onChange,
    }
  },
})
export default VCheckbox
</script>
<style scoped>
.checkbox-label {
  @apply relative flex text-base leading-5;
}
.checkbox {
  @apply appearance-none w-5 h-5 border-dark-charcoal border rounded-sm me-3 flex-shrink-0 relative;
  @apply focus:outline-none focus:ring focus:ring-offset-2 focus:ring-primary;
  @apply transition-colors disabled:bg-dark-charcoal-10 disabled:border-dark-charcoal-40;
  @apply checked:bg-dark-charcoal;
}
.checkmark {
  @apply absolute left-0 w-5 h-5 text-white;
}
</style>
