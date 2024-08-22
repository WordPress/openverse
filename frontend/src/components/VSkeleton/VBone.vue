<script setup lang="ts">
withDefaults(defineProps<{ shimmer?: boolean }>(), { shimmer: true })
</script>

<template>
  <div :class="['bg-secondary', { shimmering: shimmer }]" />
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
