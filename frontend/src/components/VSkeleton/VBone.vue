<script lang="ts">
import { defineComponent } from "vue"

export default defineComponent({
  name: "VBone",
  props: { shimmer: { type: Boolean, default: true } },
})
</script>

<template>
  <div :class="['bg-secondary', shimmer ? 'shimmering' : '']" />
</template>

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
    theme("backgroundColor.secondary") 4%,
    theme("borderColor.default") 25%,
    theme("backgroundColor.secondary") 36%
  );
  background-size: 1000px 100%;
}
</style>
