<template>
  <VIconButton
    :button-props="{ variant }"
    :icon-props="{ iconPath: closeIcon }"
    :borderless="true"
    :aria-label="label"
    @click="$emit('close')"
  />
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

import closeIcon from "~/assets/icons/close-small.svg"

export default defineComponent({
  name: "VCloseButton",
  components: { VIconButton },
  props: {
    label: {
      type: String,
      required: true,
    },
    variant: {
      type: String as PropType<
        | "filled-white"
        | "filled-white-light"
        | "filled-transparent"
        | "filled-dark"
      >,
      default: "filled-white-light",
    },
  },
  setup() {
    return {
      closeIcon,
    }
  },
})
</script>
