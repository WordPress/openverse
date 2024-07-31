<template>
  <div :class="['bg-gray-2', shimmer ? 'shimmering' : '']" />
</template>

<script lang="ts">
import { defineComponent } from "vue"

export default defineComponent({
  name: "VBone",
  props: { shimmer: { type: Boolean, default: true } },
})
</script>

<style scoped>
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.shimmering {
  animation: shimmer 3s infinite linear;
  background: linear-gradient(
    to right,
    theme("colors.gray-2") 4%,
    theme("colors.gray-3") 25%,
    theme("colors.gray-2") 36%
  );
  background-size: 1000px 100%;
}
</style>
