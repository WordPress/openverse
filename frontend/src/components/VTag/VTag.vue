<template>
  <VButton
    as="VLink"
    size="small"
    variant="filled-gray"
    class="label-bold"
    v-bind ="$props"
    v-on="$listeners"
    aria-label="Tag"
    ><slot></slot></VButton
  >
</template>

<script lang="ts">
import { defineComponent } from "vue"

import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VTag",
  components: { VButton },
  props: {
    title: {
      type: String,
      required: true,
    },
    href: {
      type: String,
      required: true,
    },
  },
})
</script>
