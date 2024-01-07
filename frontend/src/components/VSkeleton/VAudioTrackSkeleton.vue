<template>
  <article class="mb-14 flex w-full flex-row">
    <!-- Thumbnail skeleton -->
    <div
      class="shimmering mr-4 h-20 w-20 flex-shrink-0 rounded bg-dark-charcoal-10"
    />

    <div class="flex h-20 w-full flex-row gap-6">
      <!-- Track info skeleton -->
      <div class="w-70 flex-shrink-0">
        <div class="flex h-full flex-col justify-around">
          <div
            v-for="idx in 2"
            :key="idx"
            class="row-line shimmering h-3 rounded bg-dark-charcoal-10"
            :style="{ width: `${getRandomSize()}px` }"
          />
          <div class="inline-flex gap-2 space-x-1">
            <div class="shimmering h-3 w-14 rounded bg-dark-charcoal-10" />
            <div class="shimmering h-3 w-3 rounded-full bg-dark-charcoal-10" />
            <div
              class="row-line shimmering h-3 w-30 rounded bg-dark-charcoal-10"
            />
          </div>
        </div>
      </div>
      <!-- Waveform skeleton -->
      <div class="shimmering w-full rounded bg-dark-charcoal-10" />
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
    theme("colors.dark-charcoal.10") 4%,
    theme("colors.dark-charcoal.20") 25%,
    theme("colors.dark-charcoal.10") 36%
  );
  background-size: 1000px 100%;
}
</style>
