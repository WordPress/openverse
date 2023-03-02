<template>
  <div class="toggle-switch-container text-sm">
    <div class="button mr-4">
      <label for="toggle-switch" />
      <input
        id="toggle-switch"
        type="checkbox"
        class="checkbox"
        :name="name"
        :checked="checked"
        @change="onChange"
      />
      <div class="knob" />
      <div class="layer" />
    </div>
    <slot />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api"

export default defineComponent({
  name: "VToggleSwitch",
  props: {
    /**
     * Whether the toggle switch is checked or not.
     *
     * @default false
     */
    checked: {
      type: Boolean,
      required: false,
      default: false,
    },
    name: {
      type: String,
      required: false,
    },
  },
  emit: ["change"],
  setup(props, { emit }) {
    const onChange = () => {
      emit("change", { value: props.name })
    }
    return {
      onChange,
    }
  },
})
</script>

<style scoped>
.toggle-switch-container {
  display: flex;
}
.button {
  position: relative;
  width: 36px;
  height: 18px;
}
.button,
.button .layer {
  border-radius: 100px;
}
.knob {
  z-index: 2;
}
.layer {
  width: 100%;
  background-color: #ffffff;
  border: 1px solid #1e1e1e;
  z-index: 1;
  @apply ease-linear;
}
.knob,
.layer {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}
.checkbox {
  position: relative;
  width: 100%;
  height: 100%;
  padding: 0;
  margin: 0;
  opacity: 0;
  cursor: pointer;
  z-index: 3;
}
.checkbox:focus-visible ~ .layer {
  outline: 1.5px solid #c52b9b;
  outline-offset: 1px;
}
.button .knob:before {
  content: "";
  position: absolute;
  top: 3px;
  left: 4px;
  width: 12px;
  height: 12px;
  background-color: #1e1e1e;
  border-radius: 50%;
  @apply ease-linear;
}
.button .checkbox:checked + .knob:before {
  content: "";
  left: 21px;
  @apply bg-white;
}
.button .checkbox:checked ~ .layer {
  @apply bg-trans-blue;
  border: none;
}
</style>
