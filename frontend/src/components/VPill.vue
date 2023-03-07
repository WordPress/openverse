<template>
  <div
    class="w-min rounded-sm bg-yellow px-2 py-1 text-sm font-semibold uppercase"
  >
    <slot />
  </div>
</template>

<script>
import { defineComponent } from "vue"

export default defineComponent({
  name: "VPill",
})
</script>
