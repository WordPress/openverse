<script setup lang="ts">
const getRandomSize = (max = 250, min = 70) => {
  return Math.floor(Math.random() * (max - min) + min)
}
</script>

<template>
  <article class="mb-14 flex w-full flex-row">
    <!-- Thumbnail skeleton -->
    <div class="shimmering mr-4 h-20 w-20 flex-shrink-0 rounded bg-secondary" />

    <div class="flex h-20 w-full flex-row gap-6">
      <!-- Track info skeleton -->
      <div class="w-70 flex-shrink-0">
        <div class="flex h-full flex-col justify-around">
          <div
            v-for="idx in 2"
            :key="idx"
            class="row-line shimmering h-3 rounded bg-secondary"
            :style="{ width: `${getRandomSize()}px` }"
          />
          <div class="inline-flex gap-2 space-x-1">
            <div class="shimmering h-3 w-14 rounded bg-secondary" />
            <div class="shimmering h-3 w-3 rounded-full bg-secondary" />
            <div class="row-line shimmering h-3 w-30 rounded bg-secondary" />
          </div>
        </div>
      </div>
      <!-- Waveform skeleton -->
      <div class="shimmering w-full rounded bg-secondary" />
    </div>
  </article>
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
