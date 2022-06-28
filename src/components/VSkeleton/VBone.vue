<template>
  <div :class="['bg-dark-charcoal-10', shimmer ? 'shimmering' : '']" />
</template>

<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

export default defineComponent({
  name: 'VBone',
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
    theme('colors.dark-charcoal.10') 4%,
    theme('colors.dark-charcoal.20') 25%,
    theme('colors.dark-charcoal.10') 36%
  );
  background-size: 1000px 100%;
}
</style>
