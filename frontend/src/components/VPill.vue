<script lang="ts">
import { defineComponent } from "vue"

export default defineComponent({
  name: "VPill",
})
</script>

<template>
  <div
    class="w-min rounded-sm bg-complementary px-2 py-1 text-sm font-semibold uppercase"
  >
    <slot />
  </div>
</template>
