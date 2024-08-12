<template>
  <VButton
    as="VLink"
    size="small"
    has-icon-start
    class="label-bold !bg-secondary hover:!bg-tertiary hover:!text-over-dark sm:!bg-tx"
    variant="transparent-gray"
    :href="href"
  >
    <VIcon :name="iconName" />
    <span class="w-max">{{ title }}</span>
  </VButton>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

export default defineComponent({
  name: "VSourceCreatorButton",
  components: { VButton, VIcon },
  props: {
    href: {
      type: String,
      required: true,
    },
    iconName: {
      type: String as PropType<"person" | "institution">,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
  },
})
</script>
