<template>
  <article class="flex flex-row w-full mb-14">
    <!-- Thumbnail skeleton -->
    <div
      class="flex-shrink-0 h-20 w-20 mr-4 bg-dark-charcoal-10 rounded shimmering"
    />

    <div class="flex flex-row gap-6 h-20 w-full">
      <!-- Track info skeleton -->
      <div class="flex-shrink-0 w-70">
        <div class="flex flex-col h-full justify-around">
          <div
            v-for="idx in 2"
            :key="idx"
            class="row-line bg-dark-charcoal-10 h-3 rounded shimmering"
            :style="{ width: `${getRandomSize()}px` }"
          />
          <div class="inline-flex space-x-1 gap-2">
            <div class="h-3 w-14 bg-dark-charcoal-10 rounded shimmering" />
            <div class="rounded-full h-3 w-3 bg-dark-charcoal-10 shimmering" />
            <div
              class="row-line h-3 w-30 bg-dark-charcoal-10 rounded shimmering"
            />
          </div>
        </div>
      </div>
      <!-- Waveform skeleton -->
      <div class="w-full bg-dark-charcoal-10 rounded shimmering" />
    </div>
  </article>
</template>

<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

export default defineComponent({
  name: 'VAudioTrackSkeleton',
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
    theme('colors.dark-charcoal.10') 4%,
    theme('colors.dark-charcoal.20') 25%,
    theme('colors.dark-charcoal.10') 36%
  );
  background-size: 1000px 100%;
}
</style>
