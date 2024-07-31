<template>
  <article class="mb-14 flex w-full flex-row">
    <!-- Thumbnail skeleton -->
    <div class="shimmering bg-bg-fill-secondary mr-4 h-20 w-20 flex-shrink-0 rounded" />

    <div class="flex h-20 w-full flex-row gap-6">
      <!-- Track info skeleton -->
      <div class="w-70 flex-shrink-0">
        <div class="flex h-full flex-col justify-around">
          <div
            v-for="idx in 2"
            :key="idx"
            class="row-line shimmering bg-bg-fill-secondary h-3 rounded"
            :style="{ width: `${getRandomSize()}px` }"
          />
          <div class="inline-flex gap-2 space-x-1">
            <div class="shimmering bg-bg-fill-secondary h-3 w-14 rounded" />
            <div class="shimmering bg-bg-fill-secondary h-3 w-3 rounded-full" />
            <div class="row-line shimmering bg-bg-fill-secondary h-3 w-30 rounded" />
          </div>
        </div>
      </div>
      <!-- Waveform skeleton -->
      <div class="shimmering bg-bg-fill-secondary w-full rounded" />
    </div>
  </article>
</template>

<script lang="ts">
import { defineComponent } from "vue"

export default defineComponent({
  name: "VAudioTrackSkeleton",
  methods: {
    getRandomSize(max = 250, min = 70) {
      return Math.floor(Math.random() * (max - min) + min)
    },
  },
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
