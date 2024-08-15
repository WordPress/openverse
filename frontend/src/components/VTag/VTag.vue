<script lang="ts">
import { defineComponent } from "vue"

import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VTag",
  components: { VButton },
  props: {
    href: {
      type: String,
      required: true,
    },
  },
})
</script>

<template>
  <VButton
    as="VLink"
    size="small"
    variant="filled-gray"
    class="label-bold"
    v-bind="$props"
    ><slot
  /></VButton>
</template>
