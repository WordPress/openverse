<script setup lang="ts"></script>

<template>
  <div class="bg-gradient shimmering motion-reduce:!animate-none" />
</template>

<style scoped>
.bg-gradient {
  @apply bg-secondary;
  background: linear-gradient(
    to right,
    var(--color-skeleton-base) 4%,
    var(--color-skeleton-secondary) 25%,
    var(--color-skeleton-base) 36%
  );
  background-size: 1000px 100%;
}

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
}
</style>
