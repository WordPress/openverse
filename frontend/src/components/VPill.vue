<template>
  <div
    class="bg-yellow-3 w-min rounded-sm px-2 py-1 text-sm font-semibold uppercase"
  >
    <slot />
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue"

export default defineComponent({
  name: "VPill",
})
</script>
